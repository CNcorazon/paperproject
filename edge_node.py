'''
边缘节点，保存global state和区块链
'''

from queue import Queue
# from merkletools import MerkleTools
# from mpt import MerklePatriciaTrie
from edge_communicator import Communicator
# from block import Block
import hashlib
import time
import random
import zmq

# 线程：接受交易发起者的local proof请求；接受交易发起者的交易；

# 只设置一个边缘节点，暂时不考虑边缘节点之间的gossip


# # 一个分片的存储
# class EdgeNodeStorage():
#     def __init__(self, shard_id):
#         self.shard_id = shard_id

#         # 候选区块 每个分片每一轮都会产生一个区块     not sure
#         self.candidate_blocks = []

#         # 尝试不用数据库
#         # self.dbname = str(shard_id) + '.db'
#         # dbConnect(self.dbname)

#         # global state using MPT/ not sure
#         self.storage = []
#         self.global_state = MerklePatriciaTrie(self.storage)

#         self.previous_hash = 0
#         self.N = 0
#         self.gs_root = 0

#         # 分片内所有节点的公钥
#         self.public_keys = {}

#         # 先不考虑线程的问题
#         # 缓存器，用于收集修改global state的签名     not sure
#         # self.vote_buffer = Queue()

#     '''
#     每个分片主要需要做两件事，1.更新global state,区块 2.发送com给交易发起者
#     '''

#     def update_global_state(self, updata_flag):
#         # 模拟更新状态，时间消耗3s
#         # 如果块是空块，则不更新root，出块是proposalblock则更新
#         time.sleep(3)
#         if updata_flag == 1:
#             self.global_state.update(b'shard', time.time())

#     def append_block(self, blockinfo):
#         new_block = Block(blockinfo[0], blockinfo[1], blockinfo[2],
#                           blockinfo[3], blockinfo[4], blockinfo[5], blockinfo[6])
#         self.previous_hash = new_block.combine_hash_data()

#     def get_tx_com(self):
#         com = random.randint(0, 100)
#         return com

#     def get_previous_hash(self):
#         return self.previous_hash

#     def set_previous_hash(self, previous_hash):
#         self.previous_hash = previous_hash

#     def get_N(self):
#         return self.N

#     def set_N(self, num):
#         self.N = num

#     def get_gs_root(self):
#         return self.gs_root

#     def set_gs_root(self, gs_root):
#         self.gs_root = gs_root


class EdgeNode():
    def __init__(self, shard_id):
        self.shard_id = shard_id

        # 每个分片都要单独存一个账本，怎么实现呢？
        # 应该可以在上层main函数实现？

        # 这边的数据库用来存那些有local proof的交易,只设置一个边缘节点
        # 存储
        # self.dbname = '1.db'
        # 通信
        # 三个buffer分片代表，移动节点到边缘节点，边缘节点之间，边缘节点到移动节点的通信过程中用到的三个buffer
        self.VoteMsgBuffer = Queue()
        self.GossipMsgBuffer = Queue()
        self.SendMsgBuffer = Queue()
        self.communicator = Communicator(shard_id)
        # self.node_storage = EdgeNodeStorage(shard_id)

        self.vrf_list = []

    def recvmsgs(self):
        self.communicator.recv_vote(self.VoteMsgBuffer)

    def recvgossipvote(self):
        self.communicator.recv_gossipvote(self.GossipMsgBuffer)

    def sendgossipvote(self, vote):
        ip_list = ['192.168.199.212', '192.168.199.105']
        for ip in ip_list:
            self.communicator.send_gossipvote(vote, ip)

    def sendmsgs(self, vote):
        self.communicator.send_vote(vote)

    # def send_N(self):
    #     self.communicator.send_N(self.node_storage.get_N())

    # def send_previous_hash(self):
    #     self.communicator.send_previous_hash(
    #         self.node_storage.get_previous_hash())

    # def send_tx_com(self):
    #     com = self.node_storage.get_tx_com()
    #     self.communicator.send_txdigest(self.shard_id, com)

    # def send_gs_root(self):
    #     gs_root = self.node_storage.get_gs_root()
    #     self.communicator.send_gs_root(gs_root)

    # def count_vrf(self):
    #     # 在一定时间内统筹所有的proposers的vrf，返回给所有委员会成员
    #     # 这边要把所有的数据存起来
    #     info = self.communicator.recv_pro_info(self.shard_id)
    #     self.communicator.send_pro_info(self.shard_id, info)

    # def send_tx(self):
    #     self.communicator.send_tx(self.shard_id)

    # def count_vote(self):
    #     raw_info = self.communicator.recv_winner_vote(self.shard_id)
    #     # winner_id == 0 出空块
    #     hblock_flag, winner_id = self.process(raw_info)
    #     self.communicator.send_count_result(self.shard_id, hblock_flag)
    #     if hblock_flag == 1:
    #         info = self.read_winner_info(winner_id)
    #         self.communicator.send_winner_info(self.shard_id, info)


'''
    # 从交易发起者收交易
    def recv_tx(self):
        #   tx, addr = self.conmmunicator.recv_tx()
        if verify_tx():
            self.node_storage.append_tx(tx)

    def verify_tx():
        
如果有local proof则通过，没有则pass
用tee的公钥验证


    def get_local_proof(self, tx):
        (tx.get_sender_shard)

    # 将收到的带有local proof的和该分片上的账户有关的交易写进边缘节点本地数据库

    def append_tx(self, tx):
        write_tx(self.dbname, tx)

    # not sure
    def get_txs_from_db(self):
        t = get_all_txs(self.dbname)
        for i in range(len(t)):
            tx = Tx(t[i][0], t[i][1], t[i][2], t[i][5], None)
            tx.set_sig(t[i][6])
            tx.set_pubkey(t[i][8])
            self.txs[tx.md5_hash()] = t
'''
