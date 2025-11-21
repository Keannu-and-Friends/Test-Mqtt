import unittest
import time
import paho.mqtt.client as mqtt
import os
from dotenv import load_dotenv
load_dotenv()


class TestPubSubIntegration(unittest.TestCase):
    """Integration tests for pub.py and sub.py with real MQTT broker"""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures"""
        cls.broker_address = os.environ.get('MQTT_BROKER', 'mqtt')
        cls.port = int(os.environ.get('MQTT_PORT', 1883))
        cls.topic = "/test/topic/zidane"
        cls.received_messages = []
        cls.broker_available = cls._check_broker_availability()

    @classmethod
    def _check_broker_availability(cls):
        """Check if MQTT broker is available"""
        try:
            test_client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
            test_client.connect(cls.broker_address, cls.port, keepalive=5)
            test_client.disconnect()
            return True
        except Exception:
            print(
                f"Warning: MQTT Broker not available at {cls.broker_address}:{cls.port}")
            return False

    def setUp(self):
        """Set up for each test"""
        if not self.broker_available:
            self.skipTest("MQTT Broker not available")

        self.received_messages = []

    def test_publish_and_receive_message(self):
        """Test publishing and receiving a single message"""
        # Create subscriber client
        def on_message(client, userdata, msg):
            self.received_messages.append(msg.payload.decode())

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                client.subscribe(self.topic)

        subscriber = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        subscriber.on_connect = on_connect
        subscriber.on_message = on_message

        subscriber.connect(self.broker_address, self.port)
        subscriber.loop_start()

        # Give subscriber time to connect and subscribe
        time.sleep(0.5)

        # Create publisher client and send message
        publisher = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        publisher.connect(self.broker_address, self.port)
        publisher.loop_start()

        time.sleep(0.5)

        publisher.publish(
            self.topic, payload="Integration Test Message", qos=1)

        # Wait for message to be received
        time.sleep(1)

        # Cleanup
        publisher.loop_stop()
        subscriber.loop_stop()
        publisher.disconnect()
        subscriber.disconnect()

        # Assertions
        self.assertGreater(len(self.received_messages), 0)
        self.assertEqual(self.received_messages[0], "Integration Test Message")

    def test_multiple_messages(self):
        """Test publishing and receiving multiple messages"""
        received = []

        def on_message(client, userdata, msg):
            received.append(msg.payload.decode())

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                client.subscribe(self.topic)

        subscriber = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        subscriber.on_connect = on_connect
        subscriber.on_message = on_message

        subscriber.connect(self.broker_address, self.port)
        subscriber.loop_start()

        time.sleep(0.5)

        publisher = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        publisher.connect(self.broker_address, self.port)
        publisher.loop_start()

        time.sleep(0.5)

        # Publish multiple messages
        messages = ["Message 1", "Message 2", "Message 3"]
        for msg in messages:
            publisher.publish(self.topic, payload=msg, qos=1)
            time.sleep(0.2)

        # Wait for all messages
        time.sleep(1)

        # Cleanup
        publisher.loop_stop()
        subscriber.loop_stop()
        publisher.disconnect()
        subscriber.disconnect()

        # Assertions
        self.assertEqual(len(received), len(messages))
        for i, msg in enumerate(messages):
            self.assertEqual(received[i], msg)

    def test_qos_levels(self):
        """Test message delivery with different QoS levels"""
        received = []

        def on_message(client, userdata, msg):
            received.append((msg.payload.decode(), msg.qos))

        def on_connect(client, userdata, flags, rc, properties=None):
            if rc == 0:
                client.subscribe(self.topic, qos=1)

        subscriber = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        subscriber.on_connect = on_connect
        subscriber.on_message = on_message

        subscriber.connect(self.broker_address, self.port)
        subscriber.loop_start()

        time.sleep(0.5)

        publisher = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        publisher.connect(self.broker_address, self.port)
        publisher.loop_start()

        time.sleep(0.5)

        # Publish with different QoS levels
        publisher.publish(self.topic, payload="QoS 0", qos=0)
        time.sleep(0.2)
        publisher.publish(self.topic, payload="QoS 1", qos=1)
        time.sleep(0.2)

        time.sleep(1)

        # Cleanup
        publisher.loop_stop()
        subscriber.loop_stop()
        publisher.disconnect()
        subscriber.disconnect()

        # Assertions
        self.assertGreaterEqual(len(received), 1)
        self.assertIn("QoS 1", [msg[0] for msg in received])


if __name__ == '__main__':
    unittest.main()
