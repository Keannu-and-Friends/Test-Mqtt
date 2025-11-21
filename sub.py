import os, paho.mqtt.client as mqtt
from dotenv import load_dotenv

# Configuration
load_dotenv()
broker_address = os.environ.get('MQTT_BROKER')
port = int(os.environ.get('MQTT_PORT'))
topic = "/test/topic/zidane"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(topic)
    else:
        print("Failed to connect, return code %s\n", rc)


def on_message(client, userdata, msg):
    print(f"Received message from topic '{msg.topic}': {msg.payload.decode()}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

client.connect(broker_address, port)

client.loop_forever()
