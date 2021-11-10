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
    def __init__(self, shard_id, serverip):
        self.shard_id = shard_id
        self.serverip = serverip

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

        self.consensus_flag = False
        self.problock_flag = False
        self.txblock_flag = False
        self.teeproof_flag = False

        print("Connecting to server %s" % serverip)
        self.socket1 = zmq.Context().socket(zmq.REQ)
        self.socket1.connect('tcp://%s:5555' % serverip)

        # self.socket2 = zmq.Context().socket(zmq.SUB)
        # self.socket2.connect('tcp://%s:5565' % serverip)
        # self.socket2.setsockopt_string(zmq.SUBSCRIBE, '')

        # self.socket3 = zmq.Context().socket(zmq.SUB)
        # self.socket3.connect('tcp://%s:5570' % serverip)
        # self.socket3.setsockopt_string(zmq.SUBSCRIBE, '')

        # self.socket4 = zmq.Context().socket(zmq.SUB)
        # self.socket4.connect('tcp://%s:5575' % serverip)
        # self.socket4.setsockopt_string(zmq.SUBSCRIBE, '')

        # self.socket5 = zmq.Context().socket(zmq.SUB)
        # self.socket5.connect('tcp://%s:5580' % serverip)
        # self.socket5.setsockopt_string(zmq.SUBSCRIBE, '')

    def init_buffer(self):
        self.ProBlockMsgBuffer = PriorityQueue()
        self.TxBlockBuffer = PriorityQueue()
        self.TeeProofBuffer = PriorityQueue()
        self.RecvMsgBuffer = PriorityQueue()
        self.SendMsgBuffer = PriorityQueue()

    def send_msg(self, msg):
        self.socket1.send_pyobj(msg)
        msg1 = self.socket1.recv()
        # print(msg1)

    def recv_msg(self):
        # print(self.consensus_flag)
        # if self.consensus_flag:
        while not self.consensus_flag:
            continue
        socket = zmq.Context().socket(zmq.SUB)
        socket.connect('tcp://%s:5565' % self.serverip)
        socket.setsockopt_string(zmq.SUBSCRIBE, '')
        while self.consensus_flag:
            msg = socket.recv_pyobj()
            self.RecvMsgBuffer.push(msg[0], msg[1])

    def recv_problock_msg(self):
        # print('当前problockmsgbuffer中的数量为', self.ProBlockMsgBuffer.getLength())
        # if self.problock_flag:
        while not self.problock_flag:
            continue
        socket = zmq.Context().socket(zmq.SUB)
        socket.connect('tcp://%s:5570' % self.serverip)
        socket.setsockopt_string(zmq.SUBSCRIBE, '')
        while self.problock_flag:
            msg = socket.recv_pyobj()
            self.ProBlockMsgBuffer.push(msg[0], msg[1])

    def recv_txblock_msg(self):
        # if self.txblock_flag:
        while not self.txblock_flag:
            continue
        socket = zmq.Context().socket(zmq.SUB)
        socket.connect('tcp://%s:5575' % self.serverip)
        socket.setsockopt_string(zmq.SUBSCRIBE, '')
        while self.txblock_flag:
            msg = socket.recv_pyobj()
            self.TxBlockBuffer.push(msg[0], msg[1])

    def recv_TeeProof_msg(self):
        # if self.teeproof_flag:
        while not self.teeproof_flag:
            continue
        socket = zmq.Context().socket(zmq.SUB)
        socket.connect('tcp://%s:5580' % self.serverip)
        socket.setsockopt_string(zmq.SUBSCRIBE, '')
        while self.teeproof_flag:
            msg = socket.recv_pyobj()
            self.TeeProofBuffer.push(msg[0], msg[1])
