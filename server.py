import zmq
import sys
from cryptography.hazmat.primitives import serialization
from rsa_sign import *


def Recv_vote(msgs):
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    while True:
        try:
            print("wait for client ...")
            pem, sig, msg = socket.recv_multipart()
            # value = msg.decode().split(' ')[3]
            pk = serialization.load_pem_public_key(pem)
            socket.send_string('OK!')
        except Exception as e:
            print('异常:', e)
            sys.exit()


if __name__ == '__main__':
    msgs = []
    Recv_vote(msgs)
