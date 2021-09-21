'''
移动节点端网络传输接口
'''

import zmq  # 用于移动节点和边缘节点的通信
from cryptography.hazmat.primitives import serialization
from zmq.sugar import context, socket
from rsa_sign import *
import time
import sys
# _round = 5
# num = 10
# w = 50
# W = 100
# value = 0
# last_block = b'1234'
# seed = str(_round) + hashlib.sha256(last_block).hexdigest()
# sk = read_private_key()
# pi, j = Sortiiton(sk, seed, num, w, W)


class Communicator():
    def __init__(self, shard_id):
        self.shard_id = shard_id

    def send_vote(self, msg, ip):
        # 将公钥发送过去，先读取本地的pk，将RSA对象转换成字节码pem之后，再传输string
        context = zmq.Context()
        print("Connecting to server %s" % ip)
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://%s:5555" % ip)
        pk = read_public_key()
        sk = read_private_key()
        pem = pk.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        print('sending vote: ', msg)
        sig = (signing(msg[1], sk))  # 每次sig都不相同
        socket.send_multipart((pem, sig, msg[1]))
        msg1 = socket.recv()
        print(msg1)

    def recv_vote(self, ip):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        print("Collecting vote result from server %s" % ip)
        socket.connect("tcp://%s:5565" % ip)
        socket.setsockopt_string(zmq.SUBSCRIBE, '')
        pem, sig, msg = socket.recv_multipart()
        print("recvd vote from server, msg: ", msg)
        return pem, sig, msg

        # pem, sig, msg = socket.recv_multipart()
        # tmq = pem
        # while True:
        #     if time.time() - start > 10:
        #         break
        #     else:
        #         start = time.time()

        print("recv vote from server ...")
        pem, sig, msg = socket.recv_multipart()
        return pem, sig, msg
        # start = time.time()
        # if tmq == pem:
        #     continue
        # else:
        #     tmp = pem
