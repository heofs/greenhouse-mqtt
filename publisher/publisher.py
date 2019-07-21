import datetime
import json
import os
import ssl
import time
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import jwt


class Publisher(object):
    """Represents the state of a single device."""

    def __init__(self):
        self.connected = False
        load_dotenv()

        registry_id = os.getenv('REGISTRY_ID')
        cloud_region = os.getenv('CLOUD_REGION')
        self.project_id = os.getenv('PROJECT_ID')
        device_id = os.getenv('DEVICE_ID')
        self.algorithm = os.getenv('ALGORITHM')
        self.private_key_file = os.getenv('PRIVATE_KEY_FILE')
        ca_certs = os.getenv('CA_CERTS')
        mqtt_bridge_hostname = "mqtt.googleapis.com"
        mqtt_bridge_port = 8883
        jwt_expires_minutes = int(os.getenv('JWT_EXPIRES_MINUTES'))

        # Create the MQTT client and connect to Cloud IoT.
        self.client = mqtt.Client(
            client_id='projects/{}/locations/{}/registries/{}/devices/{}'.format(
                self.project_id,
                cloud_region,
                registry_id,
                device_id))
        self.client.username_pw_set(
            username='unused', password=self.create_jwt())
        self.client.tls_set(ca_certs=ca_certs,
                            tls_version=ssl.PROTOCOL_TLSv1_2)

        self.client.on_connect = self.on_connect
        self.client.on_publish = self.on_publish
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe

        self.client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

        self.client.loop_start()
        # This is the topic that the device will publish telemetry events
        # (temperature data) to.
        self.mqtt_telemetry_topic = '/devices/{}/events'.format(device_id)

        # This is the topic that the device will receive configuration updates on.
        self.mqtt_config_topic = '/devices/{}/config'.format(device_id)

        # Wait up to 5 seconds for the device to connect.
        self.wait_for_connection(5)

        # Subscribe to the config topic.
        self.client.subscribe(self.mqtt_config_topic, qos=1)

    def publish_message(self, data):
        print(data)
        payload = json.dumps(data)
        print('Publishing payload', payload)
        self.client.publish(self.mqtt_telemetry_topic, payload, qos=1)

    def wait_for_connection(self, timeout):
        """Wait for the device to become connected."""
        total_time = 0
        while not self.connected and total_time < timeout:
            time.sleep(1)
            total_time += 1

        if not self.connected:
            raise RuntimeError('Could not connect to MQTT bridge.')

    def on_connect(self, unused_client, unused_userdata, unused_flags, rc):
        """Callback for when a device connects."""
        print('Connection Result:', self.error_str(rc))
        self.connected = True

    def on_disconnect(self, unused_client, unused_userdata, rc):
        """Callback for when a device disconnects."""
        error_code = int(rc)
        if(error_code == 5 or error_code == 5):
            self.client.username_pw_set(
                username='unused', password=self.create_jwt())
        print('Disconnected:', self.error_str(rc))
        self.connected = False

    def on_publish(self, unused_client, unused_userdata, unused_mid):
        """Callback when the device receives a PUBACK from the MQTT bridge."""
        print('Published message acked.')

    def on_subscribe(self, unused_client, unused_userdata, unused_mid,
                     granted_qos):
        """Callback when the device receives a SUBACK from the MQTT bridge."""
        print('Subscribed: ', granted_qos)
        if granted_qos[0] == 128:
            print('Subscription failed.')

    def close(self):
        self.client.disconnect()
        self.client.loop_stop()
        print('Finished loop successfully. Goodbye!')

    def create_jwt(self):
        """Create a JWT (https://jwt.io) to establish an MQTT connection."""
        token = {
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'aud': self.project_id
        }
        with open(self.private_key_file, 'r') as f:
            private_key = f.read()
        print('Creating JWT using {} from private key file {}'.format(
            self.algorithm, self.private_key_file))
        return jwt.encode(token, private_key, algorithm=self.algorithm)

    def error_str(self, rc):
        """Convert a Paho error to a human readable string."""
        return '{}: {}'.format(rc, mqtt.error_string(rc))


if __name__ == '__main__':
    publisher = Publisher()
    num_messages = 10
    # Update and publish temperature readings at a rate of one per second.
    for x in range(num_messages):
        # Report the device's temperature to the server by serializing it
        # as a JSON string.
        publisher.publish_message(
            {'device_id': '', 'temperature': (x * 1.25 + 10), 'humidity': (x * 1.25 + 40)})

        time.sleep(2)

    publisher.close()
