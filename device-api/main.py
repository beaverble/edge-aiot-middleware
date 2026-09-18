import os
import requests
import json
import time
import random
from paho.mqtt import client as mqtt_client

# 자격증명·호스트는 환경변수로 주입 (실제 값은 저장소에 포함하지 않음)
API_HOST = os.getenv("AIOT_API_HOST", "HOST")
API_PORT = os.getenv("AIOT_API_PORT", "")
API_BASE = f"http://{API_HOST}:{API_PORT}"

login = {"user_id": os.getenv("AIOT_USER", ""), "password": os.getenv("AIOT_PASSWORD", "")}
get_token = requests.post(API_BASE + "/api/v1/oauth/token", data=login).json()

token1 = list(get_token.values())[0]
token2 = "bearer " + token1
access_token = {"authorization" : token2}

application = requests.get(API_BASE + "/api/v1/application", headers = access_token).json()
device = requests.get(API_BASE + "/api/v1/device", headers = access_token).json()

client_id = f'publish-{random.randint(0, 1000)}'
broker = os.getenv("MQTT_BROKER", "HOST")
port = int(os.getenv("MQTT_PORT", ""))

def connect_mqtt() -> mqtt_client:
    client = mqtt_client.Client(client_id)
    client.connect(broker, port)
    return client

def on_message(client, userdata, msg):
    print(f"Topic '{msg.topic}'에서 메시지를 받았습니다: {msg.payload.decode()}")

def edge_device_sub(client):
    for i in range(len(application)):
        for j in range(len(device)):
            if application[i]["app_id"] == device[j]["app_id"]:
                topic = application[i]["app_eui"] + "/" + device[j]["dev_eui"] + "/up"
                client.subscribe(topic)
                print(topic + "  구독 완료")

def run():
    client = connect_mqtt()
    edge_device_sub(client)
    client.on_message = on_message
    client.loop_forever()

if __name__ == '__main__':
    run()
