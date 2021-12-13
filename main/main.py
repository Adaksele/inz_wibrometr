#
__author__ = 'Adam Serocki'
__description__ = 'program jest to sterownik dla Raspberry PI dokomunikacji z ADXL45 wykorystując interfejs SPI'
__date__ = '2021'
__version__ = 'alpha 0.0.1'

# -*- coding: utf-8 -*-
# import standard libraries
from . import regs
import time
import spidev
import math
import RPi.GPIO as GPIO
import os
import datetime

#scale_factor_13b = 2 * 16 / 8192 # RANGE = +/-16g and 2^13 = 8192
#scale_factor_10b = 2 * 16 / 1024 # RANGE = =/-16g and 2^10 = 1024
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
class ADXL345():
    
    #
    # Inicjalizacja interfejsu SPI
    #
    def __init__(self, low_power = False):
        self.bus = 0     #wybór interfejsu SPI0
        self.cs  = 0     #wybór 
        self.low_power = False
        self.full_resolution = True
        self.resolution = 1
        self.range = 16 
        self.scale_factor = 2 * 16.0 / 8192.0
        self.read_mask = 0b10000000
        self.multiread_mask   = 0b01000000
        #initial fonfig
        self.spi_cfg()
        self.set_interrupts()
        self.set_data_format()
        self.set_rate()


    def spi_cfg(self):
        #self.spi.close()
        self.spi = spidev.SpiDev() # tworzy objekt spi 
        self.spi.open(self.bus, self.cs) # wybór urządzenia /dev/spidev0.0
        #spi.cshigh = False
        self.spi.max_speed_hz = 3_000_000 # częstotliwość zegara transmisji 3MHz
        self.spi.mode = 0b11
        self.spi.bits_per_word = 8
        self.spi.threewire = False

    def get_register(self, address):
        frame = []
        address |= self.read_mask
        frame.append(address)
        frame += [0]
        if debug_mode:
            print(frame)
        #self.spi.xfer2(frame)
    
    def get_registers(self, address, how_many):
        frame = []
        address |= self.read_mask
        address |= self.multiread_mask
        frame.append(address)
        frame.extend([0]*how_many)
        if debug_mode: print(frame)
        #self.spi.xfer2(frame)

    def set_register(self, address, data):
        try:
            self.spi.xfer2([address, data])
        except Exception:
            print("error set_register") 

    
    def start_measure(self):
    # użyamy tylko bit D3 uruchamiający pomiar w rejestrze POWER_CTL
        try:
            spi.xfer2([regs.REG_POWER_CTL, 0b00001000]) # Włączenie pomiaru
        except Exception:
            print("błąd uruchomienia pomiaru")
        finally:
            print()

    def stop_measure(self):
        spi.xfer2([regs.REG_POWER_CTL, 0b00000000]) # wyłączenie pomiaru

    def set_rate(self, rate = 3200, low_power = False):
 # użyamy tylko bit D3 uruchamiający pomiar
        if (rate == 3200):
            self.spi.xfer2([regs.REG_BW_RATE, 0b00001111]) 
    
    def set_data_format(self, int_invert = False, full_res = True, justify = False, range = 16):
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

        try:
            if int_invert:
                data_format |= regs.DATA_FORMAT_INT_LOW

            if full_res:
                data_format |= regs.DATA_FORMAT_FULL_RES

            if justify:
                data_format |= regs.DATA_FORMAT_JUST_LEFT

            if range == 2: 
                data_format |= regs.DATA_FORMAT_RANGE_2G
            elif range == 4: 
                data_format |= regs.DATA_FORMAT_RANGE_4G
            elif range == 8: 
                data_format |= regs.DATA_FORMAT_RANGE_8G
            elif range == 16: 
                data_format |= regs.DATA_FORMAT_RANGE_16G

            self.set_register(address, data_format)
        except Exception:
            print("błąd konfiguracji DATA_FORMAT")
        finally:
            print("\nKonfiguracja DATA_FORMAT zakończona pomyślnie\n")

    def set_interrupts(self):
        try:
            self.spi.xfer2([REG_INT_ENABLE, 0x80])       # włączenie przerwania na data ready
            self.spi.xfer2([REG_INT_MAP, 0x00])          # ustawiamy wyjscie na pin INT1   
            self.spi.xfer2([REG_INT_SOURCE, 0b10000000]) # ustawiamy zrodlo przerwania
        except Exception:
            print("błąd konfiguracji przerwania na INT1")
        finally:
            print("\nkonfiguracja przerwania INT1 zakończona pomyślnie.\n")

    def get_axes(self):
        frame = regs.REG_DATAX0 | self.read_mask | self.multiread_mask
        data = self.spi.xfer2([frame, 0, 0, 0, 0, 0, 0])
        if debug_mode: print(data)
        return data

    def convert(self, axes):
        try:
            bytes = axes
            x = bytes[0] | (bytes[1] << 8)
            if (x & (1 << 16 - 1)):
                x = x-(1 << 16)

            y = bytes[2] | (bytes[3] << 8)
            if (y & (1 << 16 - 1)):
                y = y-(1 << 16)
            
            z = bytes[4] | (bytes[5] << 8)
            if (z & (1 << 16 - 1)):
                z = z-(1 << 16)
            
            x = x*self.scale_factor
            y = y*self.scale_factor
            z = z*self.scale_factor

            print(f"x : {x}, y : {y}, z : {z}") 
        except Exception:
            print("Błąd podczas konwersji")
        finally:
            return [x, y, z]
    '''
    def set_offset(self):
        pass

    def calibration(sefl)
        pass
    '''
def read_if_interrupt():
        czujnik = ADXL345()
        czujnik.start_measure()
        _int_pin = 17
        while True:
            state = GPIO.input(_int_pin)
            if state:
                pass
            

def read_all_axes():
    print("\nWczytamy wszystkie osie\n")
    
    czujnik = ADXL345()
    n = 100
    # +X
    input("\nUstaw czujnik na +X i wciśnij Enter...\n")
    xp = []
    for i in range(n):
        xp.append(czujnik.get_axes())
    
    # -X
    input("\nUstaw czujnik na +X i wciśnij Enter...\n")
    xm = []
    for i in range (n):
        xm.append(czujnik.get_axes())
        
    # +Y
    input("\nUstaw czujnik na +X i wciśnij Enter...\n")
    xm = []
    for i in range (n):
        xm.append(czujnik.get_axes())
    # -Y
    input("\nUstaw czujnik na +X i wciśnij Enter...\n")
    xm = []
    for i in range(n):
        xm.append(czujnik.get_axes())
    # +Z
    input("\nUstaw czujnik na +X i wciśnij Enter...\n")
    xm = []
    for i in range(n):
        xm.append(czujnik.get_axes())
    # -Z
    input("\nUstaw czujnik na +X i wciśnij Enter...\n")
    xm = []
    for i in range (n):
        xm.append(czujnik.get_axes())

def read_angles():
    print("\nZbadamy zachowanie czujnika dla jednej osi przy obrocie o 360* \n")
    # 0
    # 30
    # 45
    # 90
    #120
    #180
    #240
    #300
    #360

def measure_continously(n):
    #uwaga na rejestrację czasu pomiaru!
    print(f"\nBadanie pomiaru ciągłego dla {n} próbek\n")

def damping_measure():
    print("\nBadanie tłumienia\n")



if __name__ == "__main__":
    print("runs... main.py")
    test0 = ADXL345()
    #test0.spi_cfg()
    #test0.set_interrupts()
    #test0.set_data_format()
    #test0.set_rate()
    test0.start_measure()

    duda = test0.get_axes()
    test0.convert(duda)
    #test0.get_registers(regs.REG_DATAX0, 6)
    #test0.get_register(regs.REG_DATAX0)