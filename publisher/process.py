import time
import os
from dotenv import load_dotenv
load_dotenv()

# from SHT3X import SHT3X


class SHT3X():
    def get_reading(self):
        return {"temperature": 22.4, "humidity": 55.3}


sensor = SHT3X()


def get_serial():
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
        raise Exception('Could not find serial number')


while True:
    print(os.getenv('TEST_ENV'))
    # Returns dict {"temperature": 20, "humidity": 55}
    data = sensor.get_reading()
    try:
        serialNumber = getserial()
        print(serialNumber)
    except Exception as e:
        print(e)
    print(data)
    # data['deviceid']
    time.sleep(3)
