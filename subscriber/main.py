import paho.mqtt.client as mqtt
import ssl
import random
import jwt_maker

# The callback for when the client receives a CONNACK response from the server.
root_ca = './../roots.pem'
public_crt = './../my_cert.pem'
private_key = './../my_pr.pem'

mqtt_url = "mqtt.googleapis.com"
mqtt_port = 8883
mqtt_topic = "/projects/my_project/topics/sm1"
project_id = "my_project"
cloud_region = "us-central1"
registry_id = "sm1"
device_id = "sm1"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


client = mqtt.Client("projects/{}/locations/{}/registries/{}/devices/{}".format(
    project_id,
    cloud_region,
    registry_id,
    device_id
))

client.username_pw_set(username='unused', password=jwt)

client.on_connect = on_connect
client.on_message = on_message

client.connect(host=mqtt_url, port=mqtt_port, keepalive=60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
