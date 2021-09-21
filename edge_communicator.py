'''
边缘节点端网络传输接口
'''

import zmq  # 用于移动节点和边缘节点的通信
import sys
import time
from cryptography.hazmat.primitives import serialization
from zmq.backend import Context, Socket


class Communicator():
    def __init__(self, shard_id):
        self.shard_id = shard_id

    def recv_vote(self, VoteMsgBuffer):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5555")
        while True:
            try:
                print("Thread1: wait for client's vote ...")
                pem, sig, msg = socket.recv_multipart()
                # value = msg.decode().split(' ')[3]
                # pk = serialization.load_pem_public_key(pem)
                socket.send_string('Send successfully!')
                VoteMsgBuffer.put((pem, sig, msg))
                print("Thread1: recvd vote from client!")
            except Exception as e:
                print('异常:', e)
                sys.exit()

    def send_gossipvote(self, vote, ip):
        context = zmq.Context()
        print('Thread2: gossip votes to server %s' % ip)
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://%s:5560" % ip)
        pem = vote[0]
        sig = vote[1]
        msg = vote[2]
        socket.send_multipart((pem, sig, msg))
        msg1 = socket.recv()

    def recv_gossipvote(self, GossipMsgBuffer):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5560")
        while True:
            try:
                print("Thread3: wait for server's gossipvotes ...")
                pem, sig, msg = socket.recv_multipart()
                # value = msg.decode().split(' ')[3]
                # pk = serialization.load_pem_public_key(pem)
                socket.send_string('OK!')
                # sig = sig.hex()  # 会改变验证签名的结果吗？？
                GossipMsgBuffer.put((pem, sig, msg))
                print("Thread3: recvd gossipvotes from other server!")
            except Exception as e:
                print('异常:', e)
                sys.exit()

    def send_vote(self, vote):
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind("tcp://*:5565")
        start = time.time()
        print('Thread4: send vote to client one by one')
        while time.time() < start + 6:
            pem = vote[0]
            sig = vote[1]
            msg = vote[2]
            time.sleep(1)
            socket.send_multipart((pem, sig, msg))
        print("Thread4: pub one vote end")

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
