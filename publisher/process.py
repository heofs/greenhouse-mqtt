import time
import os
import json
import paho.mqtt.client as mqtt
import ssl

from pi.device import get_device_id
from publisher import Device, create_jwt
from dotenv import load_dotenv

load_dotenv()

# from SHT3X import SHT3X
registry_id = os.getenv('REGISTRY_ID')
cloud_region = os.getenv('CLOUD_REGION')
project_id = os.getenv('PROJECT_ID')
device_id = os.getenv('DEVICE_ID')
algorithm = os.getenv('ALGORITHM')
private_key_file = os.getenv('PRIVATE_KEY_FILE')
ca_certs = os.getenv('CA_CERTS')

mqtt_bridge_hostname = os.getenv('MQTT_BRIDGE_HOSTNAME')
mqtt_bridge_port = int(os.getenv('MQTT_BRIDGE_PORT'))
num_messages = int(os.getenv('NUM_MESSAGES'))
jwt_expires_minutes = int(os.getenv('JWT_EXPIRES_MINUTES'))
message_type = os.getenv('MESSAGE_TYPE')


class SHT3X():
    def get_reading(self):
        print("getting reading from sensor...")
        return {"temperature": 22.2, "humidity": 55.5}


sensor = SHT3X()


# try:
#     device_id = 'pi' + get_device_id()
#     print("Found serial: " + device_id)
# except Exception as e:
#     raise SystemExit(e)

# device_id = "22319481358"
client = mqtt.Client(
    client_id='projects/{}/locations/{}/registries/{}/devices/{}'.format(
        project_id,
        cloud_region,
        registry_id,
        device_id))
client.username_pw_set(
    username='unused',
    password=create_jwt(
        project_id,
        private_key_file,
        algorithm))
client.tls_set(ca_certs=ca_certs, tls_version=ssl.PROTOCOL_TLSv1_2)

device = Device()

client.on_connect = device.on_connect
client.on_publish = device.on_publish
client.on_disconnect = device.on_disconnect
client.on_subscribe = device.on_subscribe
client.on_message = device.on_message

client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

client.loop_start()

# This is the topic that the device will publish telemetry events
# (temperature data) to.
mqtt_telemetry_topic = '/devices/{}/events'.format(device_id)

# This is the topic that the device will receive configuration updates on.
mqtt_config_topic = '/devices/{}/config'.format(device_id)

# Wait up to 5 seconds for the device to connect.
device.wait_for_connection(5)

# Subscribe to the config topic.
client.subscribe(mqtt_config_topic, qos=1)

while True:
    try:
        # TODO: Get sensor data
        data = sensor.get_reading()

        # TODO: Publish sensor data to sub with timestamp and device_id
        payload = json.dumps(
            {
                'deviceId': device_id,
                'location': 'living room',
                'temperature': data['temperature'],
                'humidity': data['humidity']
            }
        )
        print('Publishing payload', payload)
        client.publish(mqtt_telemetry_topic, payload, qos=1)

        time.sleep(3)
    except KeyboardInterrupt:
        print("Shutting down..")
        client.disconnect()
        client.loop_stop()
        print('Finished loop successfully.')
        break
