import zmq


def receive_data(out_addr):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(out_addr)
    print("start")

    while True:
        try:
            message = socket.recv_string()
            print("Received request:", message)

            socket.send_string("Server Start")  # 응답 전송
        except KeyboardInterrupt:
            print("Server interrupted and stopping.")
            break

if __name__ == "__main__":
    OUT_ADDR = "tcp://HOST:PORT"
    receive_data(OUT_ADDR)