import zmq
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


            source_name = data[0]
            epochtime = data[1]
            millis = data[2]
            rows = data[3]
            cols = data[4]
            pixel_size = data[5]
            compressed_image = data[6]


            decompressed_image = zstd.decompress(compressed_image)


            #print("data")
            print("Source:", source_name)
            print("Epoch Time:", epochtime)
            print("Milliseconds:", millis)
            print("Rows:", rows, "Cols:", cols)
            print("Pixel Size:", pixel_size)
            print("Decompressed Image Size:", len(decompressed_image))

        except Exception as e:
            print("error :", e)
            break


if __name__ == "__main__":
    OUT_ADDR = "tcp://HOST:PORT"
    receive_data(OUT_ADDR)
