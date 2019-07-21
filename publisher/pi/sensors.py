import smbus
import time


class SHT3X(object):
    def __init__(self):
        # Get I2C bus
        self.bus = smbus.SMBus(1)

    def get_reading(self):
        # SHT31 address, 0x44(68)
        # Send measurement command, 0x2C(44)
        # 0x06(06) High repeatability measurement
        self.bus.write_i2c_block_data(0x44, 0x2C, [0x06])

        time.sleep(0.5)

        # SHT31 address, 0x44(68)
        # Read data back from 0x00(00), 6 bytes
        # Temp MSB, Temp LSB, Temp CRC, Humididty MSB,
        # Humidity LSB, Humidity CRC
        self.data = self.bus.read_i2c_block_data(0x44, 0x00, 6)

        # Convert the data
        self.temp = self.data[0] * 256 + self.data[1]
        self.cTemp = -45 + (175 * self.temp / 65535.0)
        self.humidity = 100 * (self.data[3] * 256 + self.data[4]) / 65535.0

        # print("Temperature: %.2f C" % self.cTemp)
        # print("Relative Humidity: %.2f %%RH" % self.humidity)
        return {"temperature": self.cTemp, "humidity": self.humidity}


if __name__ == '__main__':
    sensor = SHT3X()
    sensor.get_reading()
    time.sleep(5)
    sensor.get_reading()
