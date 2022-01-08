'''
移动节点，只保存N和list（shuffle的话需要每一个块更新一次，先做个静态的）
'''

from merkletools import MerkleTools
from mobile_communicator import Communicator
from consensus import Consensus
from util import *
# import ecdsa
import config
import hashlib
from message import message
import sortition
import rsa_vrf
import binascii
import time
import pickle
import random
from CommonCoin import CommonCoin
from block import ProBlock
from rsa_sign import *
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
import logging


class MobileNode():
    def __init__(self, node_ip, shard_id, nodes, shard_num, serverip, consensus_flag):
        # 节点存储
        self.node_storage = MobileNodeStorage(
            node_ip, shard_id, nodes, shard_num)
        self.communicator = Communicator(shard_num, serverip)
        self.shard_id = shard_id
        # 私钥
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend())

        self.public_key = self.private_key.public_key()

        self.consensus = Consensus(
            self.communicator, self.node_storage, self.public_key, self.private_key, consensus_flag)

    '''
    通信模块，分为发送和接受
    '''

    def send_msg(self):
        while self.communicator.SendMsgBuffer.getLength() <= 0:
            continue
        msg = self.communicator.SendMsgBuffer.pop()
        if msg[1] != 0:
            self.communicator.send_msg(msg)

    def recv_problockmsg(self):
        while True:
            self.communicator.recv_problock_msg()

    def recv_msg(self):
        while True:
            self.communicator.recv_msg()

    def recv_txblockmsg(self):
        while True:
            self.communicator.recv_txblock_msg()

    def recv_teeproof(self):
        while True:
            self.communicator.recv_TeeProof_msg()

    def node_consensus(self):
        self.consensus.consensusrun()


class MobileNodeStorage():
    def __init__(self, node_ip, shard_id, nodes, shard_num):
        self.node_ip = node_ip
        self.shard_id = shard_id
        self.nodes = nodes
        self.shard_num = shard_num
        self.node_num = 1
        self.N = 0
        self.public_keys = {}

        self.weight = 10
        self.totalweight = 10

        self.previous_hash = '0'
        self.gs_root = b''

        self.txs = {}

        self.pi = b'0'
        self.votes = 1

        # 有MAXSTEP个列表
        self.votelist = [[], [], [], [], [], [], [], [], [], []]

        self.proposal_block = []
        self.tx_pools = []

        for _ in range(config.MAXLENGTH):
            self.proposal_block.append([])

    def set_N(self, num):
        self.N = num

    def update_list(self, public_key_list):
        self.public_keys = public_key_list

    def set_previous_hash(self, shard_id, previous_hash):
        self.previous_hash = previous_hash

    def set_pi(self, pi):
        self.pi = pi

    def set_gs_root(self, root):
        self.gs_root = root

    def set_node_num(self, num):
        self.node_num = num
