import zmq
import json
from cbor2 import loads
import zstandard as zstd

def receive_data(out_addr):

    context = zmq.Context()
    receiver_sock = context.socket(zmq.PULL)
    receiver_sock.bind(out_addr)

    print("start...")

    while True:
        try:

            cbor_stream = receiver_sock.recv()
            data = loads(cbor_stream)
            result_json = data[7]
            result_list = json.loads(result_json)
            result_list = result_list["result"]

            if len(result_list) == 0:
                pass

            else:
                for i in range(len(result_list)):
                    print("result:", result_list[i]["classType"])

        except Exception as e:
            print("error :", e)
            break

if __name__ == "__main__":
    OUT_ADDR = "tcp://HOST:PORT"
    receive_data(OUT_ADDR)
