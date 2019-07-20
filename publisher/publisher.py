import datetime
import json
import os
import ssl
import time
from dotenv import load_dotenv
import paho.mqtt.client as mqtt
import jwt

load_dotenv()

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


def create_jwt(project_id, private_key_file, algorithm):
    """Create a JWT (https://jwt.io) to establish an MQTT connection."""
    token = {
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
        'aud': project_id
    }
    with open(private_key_file, 'r') as f:
        private_key = f.read()
    print('Creating JWT using {} from private key file {}'.format(
        algorithm, private_key_file))
    return jwt.encode(token, private_key, algorithm=algorithm)


def error_str(rc):
    """Convert a Paho error to a human readable string."""
    return '{}: {}'.format(rc, mqtt.error_string(rc))


class Publisher(object):
    """Represents the state of a single device."""

    def __init__(self):
        self.temperature = 0
        self.fan_on = False
        self.connected = False

    def update_sensor_data(self):
        """Pretend to read the device's sensor data.
        If the fan is on, assume the temperature decreased one degree,
        otherwise assume that it increased one degree.
        """
        if self.fan_on:
            self.temperature -= 1
        else:
            self.temperature += 1

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
        print('Connection Result:', error_str(rc))
        self.connected = True

    def on_disconnect(self, unused_client, unused_userdata, rc):
        """Callback for when a device disconnects."""
        print('Disconnected:', error_str(rc))
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

    def on_message(self, unused_client, unused_userdata, message):
        """Callback when the device receives a message on a subscription."""
        payload = message.payload.decode('utf-8')
        print('Received message \'{}\' on topic \'{}\' with Qos {}'.format(
            payload, message.topic, str(message.qos)))

        # The device will receive its latest config when it subscribes to the
        # config topic. If there is no configuration for the device, the device
        # will receive a config with an empty payload.
        if not payload:
            return

        # The config is passed in the payload of the message. In this example,
        # the server sends a serialized JSON string.
        data = json.loads(payload)
        if data['fan_on'] != self.fan_on:
            # If changing the state of the fan, print a message and
            # update the internal state.
            self.fan_on = data['fan_on']
            if self.fan_on:
                print('Fan turned on.')
            else:
                print('Fan turned off.')


if __name__ == '__main__':
    # Create the MQTT client and connect to Cloud IoT.
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

    publisher = Publisher()

    client.on_connect = publisher.on_connect
    client.on_publish = publisher.on_publish
    client.on_disconnect = publisher.on_disconnect
    client.on_subscribe = publisher.on_subscribe
    client.on_message = publisher.on_message

    client.connect(mqtt_bridge_hostname, mqtt_bridge_port)

    client.loop_start()

    # This is the topic that the device will publish telemetry events
    # (temperature data) to.
    mqtt_telemetry_topic = '/devices/{}/events'.format(device_id)

    # This is the topic that the device will receive configuration updates on.
    mqtt_config_topic = '/devices/{}/config'.format(device_id)

    # Wait up to 5 seconds for the device to connect.
    publisher.wait_for_connection(5)

    # Subscribe to the config topic.
    client.subscribe(mqtt_config_topic, qos=1)

    # Update and publish temperature readings at a rate of one per second.
    for _ in range(num_messages):
        # In an actual device, this would read the device's sensors. Here,
        # you update the temperature based on whether the fan is on.
        publisher.update_sensor_data()

        # Report the device's temperature to the server by serializing it
        # as a JSON string.
        payload = json.dumps(
            {'temperature': publisher.temperature, 'device_id': device_id})
        print('Publishing payload', payload)
        client.publish(mqtt_telemetry_topic, payload, qos=1)
        # Send events every second.
        time.sleep(4)

    client.disconnect()
    client.loop_stop()
    print('Finished loop successfully. Goodbye!')
