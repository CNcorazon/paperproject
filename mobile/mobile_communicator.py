'''
移动节点端网络传输接口
'''

import zmq  # 用于移动节点和边缘节点的通信
from cryptography.hazmat.primitives import serialization
from zmq.sugar import context, socket
from zmq.sugar.constants import socket_types
from rsa_sign import *
from message import message
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

    def send_msg(self, msg, ip):
        context = zmq.Context()
        print("Connecting to server %s" % ip)
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://%s:5555" % ip)
        print(msg)
        socket.send_pyobj(msg)
        msg1 = socket.recv()
        print(msg1)

    def recv_msg(self, RecvMsgBuffer, ip):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        print("Collecting gossipmsg from server %s" % ip)
        socket.connect("tcp://%s:5565" % ip)
        while True:
            msg = socket.recv_pyobj()
            RecvMsgBuffer.push(msg[0], msg[1])
            socket.send_string('Send successfully!')

    def recv_problock_msg(self, ProBlockMsgBuffer, ip):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        print("Collecting problockmsg from server %s" % ip)
        socket.connect("tcp://%s:5570" % ip)
        while True:
            msg = socket.recv_pyobj()
            ProBlockMsgBuffer.push(msg[0], msg[1])
            socket.send_string('Send successfully!')

    def recv_txblock_msg(self, TxBlockBuffer, ip):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        print("Collecting txblock from server %s" % ip)
        socket.connect("tcp://%s:5575" % ip)
        while True:
            msg = socket.recv_pyobj()
            TxBlockBuffer.push(msg[0], msg[1])
            socket.send_string('Send successfully!')

    def recv_TeeProof_msg(self, TeeProofBuffer, ip):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        print("Collecting teeproof from server %s" % ip)
        socket.connect("tcp://%s:5580" % ip)
        while True:
            msg = socket.recv_pyobj()
            TeeProofBuffer.push(msg[0], msg[1])
            socket.send_string('Send successfully!')
    # def send_result(self, msg, ip):
    #     context = zmq.Context()
    #     socket = context.socket(zmq.REQ)
    #     socket.connect("tcp://%s:5575" % ip)
    #     pem = msg[0]
    #     sig = msg[1]
    #     sign_m = msg[2]
    #     print("sending vote: ", sign_m)
    #     socket.send_multipart((pem, sig, sign_m))
    #     msg1 = socket.recv()
    #     print(msg1)
    # pem, sig, msg = socket.recv_multipart()
    # tmq = pem
    # while True:
    #     if time.time() - start > 10:
    #         break
    #     else:
    #         start = time.time()

    # print("recv vote from server ...")
    # pem, sig, msg = socket.recv_multipart()
    # return pem, sig, msg
    # start = time.time()
    # if tmq == pem:
    #     continue
    # else:
    #     tmp = pem
