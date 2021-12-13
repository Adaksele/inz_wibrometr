#
__author__ = 'Adam Serocki'
__description__ = 'sterownik dla Raspberry PI do komunikacji z ADXL45 wykorystując interfejs SPI'
__date__ = '2021'
__version__ = 'beta 0.9.1'

# -*- coding: utf-8 -*-
# import lokalnych modułów
import regs
import file_management as fm
import signal_processing as sp
# import bibliotek publicznych
import time
import spidev
import queue
import csv
import math
import RPi.GPIO as GPIO
import os
import datetime
import numpy as np

# scale_factor_13b = 2 * 16 / 8192 # RANGE = +/-16g and 2^13 = 8192
# scale_factor_10b = 2 * 16 / 1024 # RANGE = =/-16g and 2^10 = 1024
#
# BIBLIOTEKA https://github.com/doceme/py-spidev
# STRONA PRODUKTU: https://www.analog.com/en/products/adxl345.html#product-overview
# DATASHEET: https://www.analog.com/media/en/technical-documentation/data-sheets/ADXL345.pdf
# https://sourceforge.net/p/raspberry-gpio-python/wiki/Inputs/
# http://tightdev.net/SpiDev_Doc.pdf
# rejestry HEX
# nastawy BINARNIE / HEX
#
debug_mode = 1


class ADXL345:

    #
    # Inicjalizacja interfejsu SPI
    #
    def __init__(self):
        self.bus = 0  # wybór interfejsu SPI0
        self.cs = 0  # wybór
        self.low_power = False
        self.full_resolution = True
        self.resolution = 13
        self.range = 16
        self.scale_factor = 2 * 16.0 / 8192.0
        #print(f"scale factor: {self.scale_factor}")
        self.read_mask = 0b10000000
        self.multiread_mask = 0b01000000
        # initial fonfig
        self.spi_cfg()
        self.set_data_format()
        self.set_interrupts()
        self.set_rate()

    def spi_cfg(self):
        try:
            self.spi = spidev.SpiDev()  # tworzy objekt spi
            self.spi.open(self.bus, self.cs)  # wybór urządzenia /dev/spidev0.0
            # spi.cshigh = False
            self.spi.max_speed_hz = 3000000  # częstotliwość zegara transmisji 3MHz
            self.spi.mode = 0b11
            self.spi.bits_per_word = 8
            self.spi.threewire = False
        except Exception:
            print("\nBłąd konfiguracji interfejsu SPI\n")
        finally:
            print("\nSPI skonfigurowane pomyślnie\n")

    def spi_close(self):
        try:
            self.spi.close()
        except Exception:
            print("\nBłąd zamykania SPI\n")
        finally:
            print("\nzamknięto interfejs spi\n")

    def start_measure(self):
        # użyamy tylko bit D3 uruchamiający pomiar w rejestrze POWER_CTL
        try:
            self.spi.xfer2([regs.REG_POWER_CTL, 0b00001000])  # Włączenie pomiaru
        except Exception:
            print("\nbłąd uruchomienia pomiaru\n")
        finally:
            print("\nUruchomino pomiar\n")

    def stop_measure(self):
        # D# na zero i zatrzymujeemy pomiar.
        try:
            self.spi.xfer2([regs.REG_POWER_CTL, 0b00000000])  # wyłączenie pomiaru
        except Exception:
            print("\nnie udało się zatrzeymać pomiaru\n")
        finally:
            print("\nzatrzymano pomiar\n")

    def set_rate(self):
        #
        try:
            self.spi.xfer2([regs.REG_BW_RATE, 0b00001111])
        except Exception:
            print("\nbłąd konfiguracji BW_RATE\n")
        finally:
            print("\nkonfiguracja BW_RATE zakończona pomyślnie\n")

    def set_data_format(self):
        # konfiguracja:
        # D7 - self test - nie uzywany
        # D6 - SPI  - korzystamy z 4wire dlatego dajemy 0
        # D5 - INT_INVERT
        # D3 - FULL_RES
        # D2 - Justify
        # D1/D0 - RANGE
        #
        address = regs.REG_DATA_FORMAT
        data_format = 0b0
        # print("\nKonfiguracja dataformat\n")
        try:
            # int_invert:
            data_format |= regs.DATA_FORMAT_INT_HIGH
            # full_res:
            data_format |= regs.DATA_FORMAT_FULL_RES
            # range == 16: 
            data_format |= regs.DATA_FORMAT_RANGE_16G
            self.set_register(address, data_format)
        except Exception:
            print("błąd konfiguracji DATA_FORMAT")
        finally:
            print("\nKonfiguracja DATA_FORMAT zakończona pomyślnie\n")

    def set_interrupts(self):
        try:
            self.spi.xfer2([regs.REG_INT_ENABLE, 0x80])  # włączenie przerwania na data ready
            self.spi.xfer2([regs.REG_INT_MAP, 0x00])  # ustawiamy wyjscie na pin INT1
            self.spi.xfer2([regs.REG_INT_SOURCE, 0b10000000])  # ustawiamy zrodlo przerwania
        except Exception:
            print("błąd konfiguracji przerwania na INT1")
        finally:
            print("\nkonfiguracja przerwania INT1 zakończona pomyślnie.\n")

    def get_axes(self):
        # frame = regs.REG_DATAX0 | self.read_mask | self.multiread_mask
        data = self.spi.xfer2([regs.REG_DATAX0 | self.read_mask | self.multiread_mask, 0, 0, 0, 0, 0, 0])
        return data

    def test_read_with_int_and_out(self, samples):
        # TODO: wysraj sie
        # TODO: wczytaj jesli INT1(pin 17) wysoki i jak zapiszesz do tablicy wystaw wysoki pin 18
        GPIO.setmode(GPIO.BCM)
        pin_in = 17
        pin_out = 25  # TODO: zmienić ten PIN 18 to C0
        GPIO.setup(pin_in, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(pin_out, GPIO.OUT)

        GPIO.output(pin_out, GPIO.LOW)
        self.stop_measure()
        self.start_measure()

        counter = 0
        t0 = time.time()
        while (counter < samples):
            # state = GPIO.input(pin_in)
            if (GPIO.input(pin_in)):
                data = self.get_axes()
                counter += 1
                # print(f"Odczytane dane:{data}")
                GPIO.output(pin_out, GPIO.HIGH)
        print(f"Czas {samples} pomiarów: {time.time() - t0}")
        self.stop_measure()

    def get_axes2(self, samples, file_name="pomiar"):
        #
        # Defining a local vars and obj.
        counter = 0
        acc = []
        frame = []
        pin_in = 11

        #Configuration GPIO for reading INT
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(pin_in, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.stop_measure()
        self.start_measure()

        adrs_masks = regs.REG_DATAX0 | self.read_mask | self.multiread_mask
        acc.append(["t", "X", "Y", "Z"])
        time_zero = time.time()
        while counter <= samples: #bedzue samples+1 bo pierwszy poiar to szum
            state = GPIO.input(pin_in)
            if state:
                data = self.spi.xfer2([adrs_masks, 0, 0, 0, 0, 0, 0])
                time_current = time.time()
                data2 = self.convert(data[1:])
                frame = [time_current]+[data2['x']]+[data2['y']]+[data2['z']]
                #print(f"get axes2: {frame}")
                acc.append(frame)
                counter += 1
        print(f"Czas {samples} pomiarów: {time.time() - time_zero}")
        self.stop_measure()
        timestamp = time.strftime("%Y%m%d") #%H:%M:%S")
        # /home/pi/python_projects/wibrometr_2020/wyniki_badan
        new_file = fm.next_path('/home/pi/python_projects/wibrometr_2020/wyniki_badan/'+timestamp+"-" + file_name + "-%s.csv")
        print(f"Nowa nazwa: {new_file}")

        with open(new_file, 'a') as csvfile:
            tmp = csv.writer(csvfile)
            for row in acc:
                #print(row)
                tmp.writerow(row)

        return acc



    def convert(self, axes):
        try:
            bytes = axes
            x = bytes[0] | (bytes[1] << 8)
            if (x & (1 << 16 - 1)):
                x = x - (1 << 16)

            y = bytes[2] | (bytes[3] << 8)
            if (y & (1 << 16 - 1)):
                y = y - (1 << 16)

            z = bytes[4] | (bytes[5] << 8)
            if (z & (1 << 16 - 1)):
                z = z - (1 << 16)

            x = x * self.scale_factor
            y = y * self.scale_factor
            z = z * self.scale_factor

            # print(f"x : {x}, y : {y}, z : {z}")
        except Exception:
            print("Błąd podczas konwersji")
        finally:
            return {"x": x, "y": y, "z": z}

    def get_register(self, address):
        frame = []
        address |= self.read_mask
        frame.append(address)
        frame + [0]
        #print(frame)
        return self.spi.xfer2(frame)

    def get_registers(self, address, how_many):
        frame = []
        address |= self.read_mask
        address |= self.multiread_mask
        frame.append(address)
        frame.extend([0] * how_many)
        return self.spi.xfer2(frame)

    def set_register(self, address, data):
        try:
            self.spi.xfer2([address, data])
        except Exception:
            print("error set_register")

    '''
    def set_offset(self):
        pass

    def calibration(sefl)
        pass

    '''

#Saleae
def read_if_interrupt():
    czujnik = ADXL345()
    GPIO.setmode(GPIO.BOARD)
    pin_in = 11
    counter = 0
    GPIO.setup(pin_in, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    q = queue.Queue()

    czujnik.stop_measure()
    czujnik.start_measure()


    t0 = time.time()
    while (counter < 3200):
        state = GPIO.input(pin_in)
        if state:
            data = czujnik.get_axes()
            q.put_nowait(data)
            counter += 1
            # print(f"Odczytane dane:{data}")
            #GPIO.output(pin_out, GPIO.HIGH)
    print(f"Czas 3200 pomiarów: {time.time() - t0}")
    czujnik.stop_measure()
    for i in range(q.qsize()):
        print(f"Kolejka: {q.get_nowait()}")
    GPIO.cleanup()

#############################################################################
#                     Część doświadczalna                                   #
#############################################################################

#Test techniczny 0 - Komunikacja z czujnikiem
def read_adxl_adress():
    print("\nTest0 - Komunikacja  czujnikiem")
    print("Pobierzemy adres fizyczny urządzenia\n")
    czujnik = ADXL345()
    adres = czujnik.spi.xfer2([0x00 | 0b10000000, 0])
    czujnik.spi_close()
    print(f"Adres adxl345: =229=  {adres}")#oczekiwane 229 0b11100101


#############################################TESTY STATYCZNE#################################

#Test 1 - Sprawdzenie podstawowej fukncjonalności czujnika
# Odczyt z każdej osi
def read_all_axes():
    print("\nWczytamy wszystkie osie\n")

    czujnik = ADXL345()
    n = 100

    # +X
    input("\nUstaw czujnik na +X i wciśnij Enter...\n")
    xp = czujnik.get_axes2(n, "xp")

    # -X
    input("\nUstaw czujnik na -X i wciśnij Enter...\n")
    xm = czujnik.get_axes2(n, "xm")

    # +Y
    input("\nUstaw czujnik na +Y i wciśnij Enter...\n")
    yp = czujnik.get_axes2(n, "yp")
    
    # -Y
    input("\nUstaw czujnik na -Y i wciśnij Enter...\n")
    ym = czujnik.get_axes2(n, "ym")
    # +Z
    input("\nUstaw czujnik na +Z i wciśnij Enter...\n")
    zp = czujnik.get_axes2(n, "zp")
    # -Z
    input("\nUstaw czujnik na -Z i wciśnij Enter...\n")
    zm = czujnik.get_axes2(n, "zm")
    #wyłączenie SPI pod koniec metody`
    czujnik.spi_close()

# Test 2 - Skalowalność, badanie wektora przyspieszenia
# Pomiary w polu grawitacyjnym, gdzie czujnik zmienia kąt położenia względem przyspieszenia grawitacyjnego.
def read_angles():
    print("+========================================================================+")
    print("|            Zbadamy zachowanie czujnika przy obrocie o 360*             |")
    print("+========================================================================+")
    angles = [0, 30, 45, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330, 360]

    czujnik = ADXL345()
    n = 100

    for angle in angles:
        input(f"Ustaw obrotnicę na kąt {str(angle)} i wciśnij Enter...\n")
        czujnik.get_axes2(n,"kat-"+str(angle))

    #wylaczenie interfejsu SPI
    czujnik.spi_close()
################################### TESTY DYNAMICZNE ###########################
#
#Test 0 - Pomiar Drgań wygaszanych. Badanie drgania listwy przytwierdzonej do stołu.
def damping_measure():
    print("\nBadanie tłumienia\n")
    #n = 8192
    s = input("Ile sekund ma trwać pomiar tłumienia?")
    fs = 3200
    n = int(s) * fs
    file_name = "tłumienie"
    czujnik = ADXL345()
    data = czujnik.get_axes2(n, file_name)
    czujnik.stop_measure()
    czujnik.spi_close()

def measure_continously():
    # uwaga na rejestrację czasu pomiaru!
    print(f"\nBadanie pomiaru ciągłego dla podanego czasu\n")
    s = input("Ile sekund ma trwać pomiar?")
    fs = 3200
    n = int(s) * fs
    file_name = "pelnowymiarowy_35"
    czujnik = ADXL345()
    data = czujnik.get_axes2(n, file_name)
    czujnik.stop_measure()
    czujnik.spi_close()

    signal_x = list(map(lambda x: x[1], data))
    signal_y = list(map(lambda x: x[2], data))
    signal_z = list(map(lambda x: x[3], data))
    #print(signal_z)
    print(f"Freq X: {sp.signal_fft(signal_x[2:])}")
    print(f"Freq Y: {sp.signal_fft(signal_y[2:])}")
    print(f"Freq Z: {sp.signal_fft(signal_z[2:])}")

    print("Phase diff: \n")
    sp.diff(signal_x[2:], signal_y[2:], signal_z[2:])


def main():
    pass
    print("Wybierz co chcesz zrobić: ")
    print("1 Odczytać pomiary ze wszystkich osi")
    print("2 Odczytać pomiar dla wartości konta")
    print("3 Dokonać pomiaru ciągego")
    print("4 Dokonać badania tłumienia")
    choice = input("co chcesz zrobić? ")
    if (choice == 1):
        pass
    if (choice == 2):
        pass
    if (choice == 3):
        print("\n Ile sekund ma trwać pomiar?")

    if (choice == 4):
        pass


if __name__ == "__main__":
    print("runs... main.py")
    read_adxl_adress()
    #read_all_axes()
    #read_angles()
    #damping_measure()
    measure_continously()
    #read_if_interrupt()
    #czujnik = ADXL345()
    #czujnik.get_axes2(10, "test_0")
    #czujnik.test_read_with_int_and_out(250)
