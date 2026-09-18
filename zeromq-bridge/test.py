import requests
import json
import random
import configparser
import logging , datetime
import ast
import base64
from collections import OrderedDict

from paho.mqtt import client as mqtt_client

logging.basicConfig(filename="./log_file.txt", level=logging.DEBUG,
                    format="[ %(asctime)s | %(levelname)s ] %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S")

logger = logging.getLogger()

config = configparser.ConfigParser()
config.read('python_config.ini')

user_id = config['edgeGWAPI']['user_id']
password = config['edgeGWAPI']['password']
GWAPI_host = config['edgeGWAPI']['host']
GWAPI_port = config['edgeGWAPI']['port']

edgeGW_mqtt = config['edgeGW_mqtt']['host']
edgeGW_mqtt_port = config['edgeGW_mqtt']['port']

incoming_mqtt = config['incoming_mqtt']['host']
incoming_mqtt_port = config['incoming_mqtt']['port']

login = {"user_id" : user_id, "password" : password}
get_token = requests.post(GWAPI_host + ":" + GWAPI_port + "/api/v1/oauth/token", data=login).json()

token = list(get_token.values())[0]
token2 = "bearer " + token

access_token = {"authorization" : token2}

app_ini= config['app']['app_list']
application_list = ast.literal_eval(app_ini)

application = requests.get(GWAPI_host + ":" + GWAPI_port + "/api/v1/application", headers = access_token).json()
device = requests.get(GWAPI_host + ":" + GWAPI_port + "/api/v1/device", headers = access_token).json()

client_id = f'publish-{random.randint(0, 1000)}'


def preprocess(msg):
    msg = msg.replace("false", "'False'")
    msg_dict = ast.literal_eval(msg)
    decode_payload = base64.b64decode(msg_dict['payload'])
    hex_string = decode_payload.hex()
    hex_string = hex_string[16:]
    encoded_tlv = bytes.fromhex(hex_string)

    return encoded_tlv


def tlv_decode(encoded_tlv):
    decoded_list = []
    i = 0
    while i < len(encoded_tlv) - 1:
        try:
            type = int(encoded_tlv[i + 1])
            length = int(encoded_tlv[i] - 192)
            value_bytes = encoded_tlv[i + 2:i + 2 + length]
            if type != 5:
                value = value_bytes.decode('utf-8')
            if type == 5:
                value = int(value_bytes.hex(), 16)

        except:
            print('TLV message Error!')
            logger.info("TLV message Error!")
            return None

        decoded_list.append((type, value))
        i += 2 + length

    return decoded_list


def publish(topic, client, message):
    result, _ = client.publish(topic, message)
    if result == mqtt_client.MQTT_ERR_SUCCESS:
        pass
    else:
        print("메시지 발행(Publish) 실패")
        logger.info("메시지 발행(Publish) 실패")


def json_msg(topic, decoded_list):
    # print(topic)
    dev_eui = topic.split('/')[1]
    # dev_eui = topic[17:33]
    print(dev_eui)
    for i in range(len(device)):
        if dev_eui == device[i]["dev_eui"]:
            break

    data = OrderedDict()
    data["name"] = device[i]["dev_id"]  # device_id
    data["cmd"] = "DeviceDataReport"
    data["DeviceDataReport"] = {"PM10": decoded_list[0][1], "PM25": decoded_list[1][1],
                                "Temperature": decoded_list[2][1], "Humidity": decoded_list[3][1],
                                "ErrorCode": decoded_list[4][1], "Timestamp": int(decoded_list[5][1])}

    data_json = json.dumps(data, ensure_ascii=False, indent="\t")

    return data_json


def connect_incoming_mqtt():
    client = mqtt_client.Client(client_id)
    try:
        client.connect(incoming_mqtt, int(incoming_mqtt_port))
        print("incoming MQTT 연결")
        print("*************************************************************************")
        return client
    except:
        print("Incoming MQTT Broker 연결 불가")
        logger.info("Incoming MQTT Broker 연결 불가")


def connect_edgeGW_mqtt():
    client = mqtt_client.Client(client_id)
    try:
        client.connect(edgeGW_mqtt, int(edgeGW_mqtt_port))
        print('EdgeGW MQTT 연결')
        print("*************************************************************************")
        return client
    except:
        print("EdgeGW MQTT Broker 연결 불가")
        logger.info("EdgeGW MQTT Broker 연결 불가")


def edge_device_sub(client):
    app_num = len(application_list)
    for i in range(len(application)):
        found = False
        for k in range(len(application_list)):
            if application[i]["app_id"] == application_list[k]:
                found = True
                break;
        if found:
            for j in range(len(device)):
                if application[i]["app_id"] == device[j]["app_id"]:
                    topic = application[i]["app_eui"] + "/" + device[j]["dev_eui"] + "/up"
                    client.subscribe(topic)
                    print(topic + "  구독 완료")
                    logger.info(topic + "  구독 완료")
    print("*************************************************************************")


def on_message(client, userdata, msg):
    print(f"Topic '{msg.topic}'에서 메시지를 받았습니다: {msg.payload.decode()}")
    print("*************************************************************************")
    logger.info(f"Topic '{msg.topic}'에서 메시지를 받았습니다: {msg.payload.decode()}")

    decode_payload = preprocess(msg.payload.decode())
    decode_tlv = tlv_decode(decode_payload)

    if decode_tlv == None:
        print("Message Drop")

    else:
        pub_msg = json_msg(msg.topic, decode_tlv)
        publish("DataTopic", client, pub_msg)
        print(f"메시지를 발행(Publish)했습니다: {pub_msg}")
        print("*************************************************************************")
        logger.info(f"메시지를 발행(Publish)했습니다: {pub_msg}")


def run():
    in_client = connect_incoming_mqtt()
    edge_device_sub(in_client)
    in_client.on_message = on_message
    in_client.loop_forever()

    out_client = connect_edgeGW_mqtt()
    out_client.loop_forever()

if __name__ == '__main__':
    run()