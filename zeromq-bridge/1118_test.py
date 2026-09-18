import json
import zmq
import random
from paho.mqtt import client as mqtt_client
from cbor2 import loads
from collections import OrderedDict

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("MQTT broker connect")
        else:
            print(f"MQTT broker connect fail: {rc}")

    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(mqtt, mqtt_port)
    return client

def publish(topic, client, message):
    result, _ = client.publish(topic, message)
    if result == mqtt_client.MQTT_ERR_SUCCESS:
        print(f"message Publish : {message}")
    else:
        print(f"message Publish Fail : {message}")

def run(data):
    client = connect_mqtt()
    client.loop_start()
    publish(client, data)
    client.loop_stop()

def receive_data(out_addr):
    context = zmq.Context()

    receiver_sock = context.socket(zmq.PULL)
    receiver_sock.bind(out_addr)

    print("socket connect...")

    cbor_stream = receiver_sock.recv()
    data = loads(cbor_stream)

    source_name = data[0]
    epochtime = data[1]
    result = data[7]

    return source_name, epochtime, result

def json_msg(name,time,result):
    result_list = json.loads(result)
    result_list = result_list["result"]
    if len(result_list) == 0:
        pass
    else:
        for i in range(len(result_list)):
            #print("result:", result_list[i]["classType"])
            data = OrderedDict()
            data["name"] = str("CCTV_") + str(name)
            data["cmd"] = "CCTVDetectionReport",
            data["CCTVDetectionReport"] = {"CameraNo": str("CCTV_") + str(name), "ClassType": result_list[i]["classType"],
                                        "Box": result_list[i]["box"], "Confidence": result_list[i]["confidence"],"DetectionTime": time}

            data_json = json.dumps(data, ensure_ascii=False, indent="\t")

            print(data_json)

if __name__ == "__main__":
    OUT_ADDR = "tcp://HOST:PORT"
    mqtt = 'HOST'
    mqtt_port = 'PORT'
    client_id = f'publish-{random.randint(0, 1000)}'
    topic = "DataTopic"

    while True:
        s_name, s_time, s_result = receive_data(OUT_ADDR)
        json_msg(s_name,s_time,s_result)

