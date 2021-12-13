import spidev

#def main():

spi = spidev.SpiDev()
print("spi zainiclajozowane")
spi.open(0,1)
spi.max_speed_hz = 3000000
spi.mode = 0b11
spi.bits_per_word = 8
spi.threewire = False

spi.close()
print("spi zamknięte")