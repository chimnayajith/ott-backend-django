# mqtt.py
import paho.mqtt.client as mqtt
import paho.mqtt.publish as mqtt_publish
import json

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("notification_topic")

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload.decode())
    print(f"Received message: {payload}")

    
    process_received_message(payload)

def process_received_message(payload):
    
    print(f"Custom processing: {payload}")

    
    response_payload = {'response': 'Processed successfully'}
    mqtt_publish.single('response_topic', json.dumps(response_payload), hostname='localhost')

def start_mqtt_listener():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect("localhost", 1883, 60)

    client.loop_start()
