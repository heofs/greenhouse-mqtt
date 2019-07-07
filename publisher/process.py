import time
import os
from dotenv import load_dotenv
load_dotenv()

# from SHT3X import SHT3X


class SHT3X():
    def get_reading(self):
        return {"temperature": 22.4, "humidity": 55.3}


sensor = SHT3X()


def get_device_serial():
    # Extract serial from cpuinfo file
    cpuserial = "0000000000000000"
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        f.close()
        return cpuserial
    except:
        raise Exception('Exception: Could not find serial number')


# try:
#     device_serial = get_device_serial()
#     print("Found serial: " + device_serial)
# except Exception as e:
#     raise SystemExit(e)

device_serial = "22319481358"

while True:
    # TODO: Get sensor data
    data = sensor.get_reading()
    res = {
        'deviceId': device_serial,

    }

    # TODO: Publish sensor data to sub with timestamp and device_serial

    # TODO: Wait for X seconds.
    time.sleep(10)

    print(os.getenv('TEST_ENV'))
    # Returns dict {"temperature": 20, "humidity": 55}
    print(data)
    # data['deviceid']
