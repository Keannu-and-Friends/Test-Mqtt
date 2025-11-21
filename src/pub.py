import time
import os
import paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Configuration
load_dotenv()
broker_address = os.environ.get('MQTT_BROKER')
port = int(os.environ.get('MQTT_PORT'))
topic = "/test/topic/zidane"


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %s\n", rc)


def on_publish(client, userdata, mid, properties, reason_code=None):
    print("Message Published")


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_publish = on_publish

client.connect(broker_address, port)

client.loop_start()

# Publish a message
while True:
    client.publish(topic, payload="Hello World!", qos=1)
    time.sleep(4)
