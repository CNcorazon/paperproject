'''
边缘节点端网络传输接口
'''
import logging
import zmq  # 用于移动节点和边缘节点的通信
import sys
import time
import random
from cryptography.hazmat.primitives import serialization
from zmq.backend import Context, Socket
from zmq.sugar import context, socket
from message import *
from util import PriorityQueue

# logging.basicConfig(
#     format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO, filemode='w', filename='server_communicator.log')


class Communicator():
    def __init__(self, shard_id, iplist):
        self.shard_id = shard_id
        self.iplist = iplist

        # 消息接受Buffer
        self.RecMsgBuffer = PriorityQueue()
        self.SendMsgBuffer = PriorityQueue()

        # 由服务器生成的信息，对应的发送buffer
        self.ProBlockMsgBuffer = PriorityQueue()
        self.TxBlockMsgBuffer = PriorityQueue()
        self.TeeProofMsgBuffer = PriorityQueue()

        # 服务器中的三个模块的消息处理buffer
        self.AppendBlockSigBuffer = PriorityQueue()
        self.TxBlockSigBuffer = PriorityQueue()
        self.TeeProofSigBuffer = PriorityQueue()

        # 服务器之间同步用的buffer
        self.SysnMsgBuffer = PriorityQueue()

        self.socket1 = zmq.Context().socket(zmq.REP)
        self.socket1.bind('tcp://*:5555')

        self.socket2 = zmq.Context().socket(zmq.PUB)
        self.socket2.bind('tcp://*:5565')

        self.socket3 = zmq.Context().socket(zmq.PUB)
        self.socket3.bind('tcp://*:5570')

        self.socket4 = zmq.Context().socket(zmq.PUB)
        self.socket4.bind('tcp://*:5575')

        self.socket5 = zmq.Context().socket(zmq.PUB)
        self.socket5.bind('tcp://*:5580')

        # 服务器之间的广播
        self.socket6 = []
        for ip in iplist:
            socket = zmq.Context().socket(zmq.REQ)
            socket.connect('tcp://%s:5555' % ip)
            self.socket6.append(socket)

    def init_buffer(self):
        self.AppendBlockSigBuffer = PriorityQueue()
        self.TxBlockSigBuffer = PriorityQueue()
        self.TeeProofSigBuffer = PriorityQueue()
        self.TxBlockMsgBuffer = PriorityQueue()
        # self.TeeProogMsgBuffer = PriorityQueue()

    def recv_msg(self):
        # context = zmq.Context()
        # socket = context.socket(zmq.REP)
        # socket.bind("tcp://*:5555")
        while True:
            try:
                msg = self.socket1.recv_pyobj()
                # value = msg.decode().split(' ')[3]
                # pk = serialization.load_pem_public_key(pem)
                self.socket1.send_string('Send successfully!')
                self.RecMsgBuffer.push(msg[0], msg[1])
                logging.info("RecvMsgThread: recvd msg from client!")
            except Exception as e:
                print('异常:', e)
                sys.exit()

    def send_msg(self, msg):
        if msg[1] != 0:
            # context = zmq.Context()
            # socket = context.socket(zmq.REQ)
            # socket.bind("tcp://*:5565")
            # socket.send_pyobj(msg)
            # logging.info("SendMsgThread: sent msg to client!")
            # msg1 = socket.recv()
            self.socket2.send_pyobj(msg)

    def send_gossipmsg(self, msg):
        if msg[1] != 0:
            for socket in self.socket6:
                socket.send_pyobj(msg)
                msg1 = socket.recv()

    def send_problockmsg(self, msg):
        if msg[1] != 0:
            # context = zmq.Context()
            # socket = context.socket(zmq.REQ)
            # socket.bind("tcp://*:5570")
            # logging.info('SendProblockThread: sending one problockmsg')
            # # print(msg)
            # socket.send_pyobj(msg)
            # msg1 = socket.recv()
            # print(msg1)
            self.socket3.send_pyobj(msg)

    def send_txblockmsg(self, msg):
        if msg[1] != 0:
            # context = zmq.Context()
            # socket = context.socket(zmq.REQ)
            # socket.bind("tcp://*:5575")
            # socket.send_pyobj(msg)
            # msg1 = socket.recv()
            # print(msg1)
            self.socket4.send_pyobj(msg)

    def send_teeproofmsg(self, msg):
        if msg[1] != 0:
            # context = zmq.Context()
            # socket = context.socket(zmq.REQ)
            # socket.bind("tcp://*:5580")
            # socket.send_pyobj(msg)
            # msg1 = socket.recv()
            # print(msg1)
            self.socket5.send_pyobj(msg)

    # def recv_gossipmsg(self, RecMsgBuffer):
    #     context = zmq.Context()
    #     socket = context.socket(zmq.REP)
    #     socket.bind("tcp://*:5560")
    #     while True:
    #         try:
    #             print("Thread3: wait for server's gossipvotes ...")
    #             msg = socket.recv_pyobj()
    #             # value = msg.decode().split(' ')[3]
    #             # pk = serialization.load_pem_public_key(pem)
    #             socket.send_string('OK!')
    #             # sig = sig.hex()  # 会改变验证签名的结果吗？？
    #             RecMsgBuffer.put(msg)
    #             print("Thread3: recvd gossipvotes from other server!")
    #         except Exception as e:
    #             print('异常:', e)
    #             sys.exit()

    # 发送消息时，将对应的权重和总权重发送给移动节点

        # while time.time() < start + 6:
        #     # pem = vote[0]
        #     # sig = vote[1]
        #     # msg = vote[2]
        #     weight = vote[3].to_bytes(
        #         length=4, byteorder='little', signed=False)
        #     totalweight = vote[4].to_bytes(
        #         length=4, byteorder='little', signed=False)
        #     time.sleep(1)
        #     socket.send_multipart((pem, sig, msg, weight, totalweight))
        # print("Thread4: pub one vote end")

    def recv_result(self, ResultMsgBuffer):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5570")
        while True:
            try:
                print("Thread5: wait for proposal result ...")
                pem, sig, sign_m = socket.recv_multipart()
                socket.send_string("OK!")
                ResultMsgBuffer.put((pem, sig, sign_m))
                print("Thread5: recvd proposal result from nodes!")
            except Exception as e:
                print("异常：", e)
                sys.exit()

    # def send_N(self, num):
    #     # 服务器发送N，可能应该写在服务器上
    #     return None

    # def send_previous_hash(self, previous_hash):
    #     return None

    # def send_gs_root(self, gs_root):
    #     return None

    # def send_txdigest(self, shard_id, com):
    #     # 服务器发送交易的摘要
    #     return None

    # def send_tx(self, shard_id):
    #     # 服务器发送交易
    #     return None

    # def send_pro_info(self, shard_id, info):
    #     # 共识期间，每个委员会成员读取proposers的VRF，选出最低VRF proposer作为出块者，获得他的com
    #     return None

    # def send_count_result(self, shard_id, flag):
    #     return None

    # def send_winner_info(self, shard_id, winner_info):
    #     return None

    # def recv_pro_info(self, shard_id):
    #     # 从client读取pro_info
    #     info = []
    #     return info

    # def recv_winner_vote(self, shard_id):
    #     info = []
    #     return info
