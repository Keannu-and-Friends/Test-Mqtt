from src import pub
import unittest
from unittest.mock import patch, MagicMock
import os


class TestPubSubMock(unittest.TestCase):
    """Unit tests for pub.py and sub.py with mocked MQTT broker"""

    @patch('src.pub.time.sleep')
    @patch('paho.mqtt.client.Client')
    @patch.dict(os.environ, {
        'MQTT_BROKER': 'mqtt',
        'MQTT_PORT': '1883'
    })
    def test_publisher_connects_and_publishes(self, mock_client_class, mock_sleep):
        """Test that publisher connects to broker and publishes messages"""
        # Setup mock client
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock the infinite loop to break after one iteration
        mock_sleep.side_effect = [None, KeyboardInterrupt()]

        try:
            pub.main()
        except KeyboardInterrupt:
            pass

        # Verify connection was called
        mock_client.connect.assert_called_once_with('mqtt', 1883)

        # Verify loop_start was called
        mock_client.loop_start.assert_called_once()

        # Verify callbacks were set
        self.assertIsNotNone(mock_client.on_connect)
        self.assertIsNotNone(mock_client.on_publish)

    @patch('paho.mqtt.client.Client')
    def test_on_connect_success(self, mock_client_class):
        """Test on_connect callback with successful connection"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Call on_connect with rc=0 (success)
        with patch('builtins.print') as mock_print:
            pub.on_connect(mock_client, None, {}, 0)
            mock_print.assert_called_once_with("Connected to MQTT Broker!")

    @patch('paho.mqtt.client.Client')
    def test_on_connect_failure(self, mock_client_class):
        """Test on_connect callback with failed connection"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Call on_connect with rc=1 (failure)
        with patch('builtins.print') as mock_print:
            pub.on_connect(mock_client, None, {}, 1)
            mock_print.assert_called_once()

    @patch('paho.mqtt.client.Client')
    def test_on_publish_callback(self, mock_client_class):
        """Test on_publish callback"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        with patch('builtins.print') as mock_print:
            pub.on_publish(mock_client, None, 1, None)
            mock_print.assert_called_once_with("Message Published")

    @patch('src.pub.time.sleep')
    @patch('paho.mqtt.client.Client')
    @patch.dict(os.environ, {
        'MQTT_BROKER': 'localhost',
        'MQTT_PORT': '1883'
    })
    def test_publish_message_format(self, mock_client_class, mock_sleep):
        """Test that messages are published with correct format"""
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Mock the infinite loop to break after one iteration
        mock_sleep.side_effect = KeyboardInterrupt()

        try:
            pub.main()
        except KeyboardInterrupt:
            pass

        # The module publishes in a loop, so check if publish was called
        mock_client.publish.assert_called()

        # Verify the call arguments
        call_args = mock_client.publish.call_args
        self.assertEqual(call_args[0][0], "/test/topic/zidane")  # topic
        self.assertEqual(call_args[1]['payload'], "Hello World!")  # payload
        self.assertEqual(call_args[1]['qos'], 1)  # QoS level


if __name__ == '__main__':
    unittest.main()
