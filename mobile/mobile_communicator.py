'''
移动节点端网络传输接口
'''

import zmq  # 用于移动节点和边缘节点的通信
from cryptography.hazmat.primitives import serialization
from zmq.sugar import context, socket
from zmq.sugar.constants import socket_types
from rsa_sign import *
from message import message
from util import PriorityQueue
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

        # 发送接收移动节点gossip的消息buffer
        self.SendMsgBuffer = PriorityQueue()
        self.RecvMsgBuffer = PriorityQueue()

        # 接收服务器生成的消息buffer
        # # 1）发送创建problock所需的信息来创建problock
        self.ProBlockMsgBuffer = PriorityQueue()
        # 2）接收各个candidate创建的problock
        # self.ProBlcokBuffer = PriorityQueue()
        # # 3) 接收reduction结果
        # self.ReductionBuffer = PriorityQueue()
        # 4）接收txblock
        self.TxBlockBuffer = PriorityQueue()
        # 5）接收交易区块验证proof
        self.TeeProofBuffer = PriorityQueue()

    def init_buffer(self):
        self.ProBlockMsgBuffer = PriorityQueue()
        self.TxBlockBuffer = PriorityQueue()
        self.TeeProofBuffer = PriorityQueue()
        self.RecvMsgBuffer = PriorityQueue()
        self.SendMsgBuffer = PriorityQueue()

    def send_msg(self, msg, ip):
        context = zmq.Context()
        # print("Connecting to server %s" % ip)
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://%s:5555" % ip)
        socket.send_pyobj(msg)
        msg1 = socket.recv()
        # print(msg1)

    def recv_msg(self, ip):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        print("Collecting gossipmsg from server %s" % ip)
        socket.connect("tcp://%s:5565" % ip)
        while True:
            msg = socket.recv_pyobj()
            self.RecvMsgBuffer.push(msg[0], msg[1])
            # print('recvmsgbuffer length is:', self.RecvMsgBuffer.getLength())
            socket.send_string('Send successfully!')

    def recv_problock_msg(self, ip):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        print("Collecting problockmsg from server %s" % ip)
        socket.connect("tcp://%s:5570" % ip)
        while True:
            msg = socket.recv_pyobj()
            self.ProBlockMsgBuffer.push(msg[0], msg[1])
            socket.send_string('Send successfully!')

    def recv_txblock_msg(self, ip):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        print("Collecting txblock from server %s" % ip)
        socket.connect("tcp://%s:5575" % ip)
        while True:
            msg = socket.recv_pyobj()
            self.TxBlockBuffer.push(msg[0], msg[1])
            socket.send_string('Send successfully!')

    def recv_TeeProof_msg(self, ip):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        print("Collecting teeproof from server %s" % ip)
        socket.connect("tcp://%s:5580" % ip)
        while True:
            msg = socket.recv_pyobj()
            self.TeeProofBuffer.push(msg[0], msg[1])
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
