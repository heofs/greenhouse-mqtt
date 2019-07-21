import time
import os
import json
import paho.mqtt.client as mqtt
import ssl
from datetime import datetime

from pi.device import get_device_id
from pi.sensors import SHT3X
from publisher import Publisher


# class SHT3X():
#     def get_reading(self):
#         print("getting reading from sensor...")
#         return {"temperature": 22.2, "humidity": 55.5}


sensor = SHT3X()
publisher = Publisher()
device_id = 'test-device'


# try:
#     device_id = 'pi' + get_device_id()
#     print("Found serial: " + device_id)
# except Exception as e:
#     raise SystemExit(e)

# device_id = "22319481358"


while True:
    try:
        # TODO: Get sensor data
        data = sensor.get_reading()
        # TODO: Publish sensor data to sub with timestamp and device_id
        payload = {
            'device_id': device_id,
            'location': 'living room',
            'temperature': data['temperature'],
            'humidity': data['humidity']
        }
        publisher.publish_message(payload)
        time.sleep(5)

    except KeyboardInterrupt:
        print("Shutting down..")
        publisher.close()
        print('Finished loop successfully.')
        break
