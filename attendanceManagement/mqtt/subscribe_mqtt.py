import os
import threading
from paho.mqtt import client as mqtt_client
from attendanceManagement.mqtt import config_mqtt
from attendanceManagement.control_logic import json_decorder


broker = config_mqtt.broker
port = config_mqtt.port
topic = config_mqtt.topic
client_id = config_mqtt.client_id
username = config_mqtt.username
password = config_mqtt.password

script_dir = os.path.dirname(os.path.realpath(__file__))
cert_path = os.path.join(script_dir, 'emqxsl-ca.crt')


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print(f"Failed to connect, return code {rc}")

    client = mqtt_client.Client(client_id)
    client.tls_set(ca_certs=cert_path)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        #json_decorder.json_decorator(msg.payload.decode())

    client.subscribe(topic)
    client.on_message = on_message


def mqtt_loop():
    client = connect_mqtt()
    subscribe(client)
    client.loop_forever()


def start_mqtt_thread():
    mqtt_thread = threading.Thread(target=mqtt_loop)
    mqtt_thread.daemon = True
    mqtt_thread.start()

