import zmq
import sys
from cryptography.hazmat.primitives import serialization

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
while True:
    try:
        print("wait for client ...")
        pem = socket.recv_string()
        pk = serialization.load_pem_public_key(pem)
        print(pk)
        socket.send_string('OK!')
    except Exception as e:
        print('异常:', e)
        sys.exit()
