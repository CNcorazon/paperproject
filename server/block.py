"""
区块类
"""

from rsa_sign import signing
import hashlib
import random
import sys
import ecdsa
from cryptography.hazmat.primitives import serialization


class ProBlock:
    def __init__(
        self,
        shard_id,  # 分片编号
        shard_length,  # 分片长度
        previous_hash,  # 第N-1个区块的哈希
        txlist_N_2_hash,  # 第N-2个区块中包含的交易区块列表哈希
        # 第N-5个区块对应的merkleroot([merkleroot,N,sig1,sig2,sig3,sig4......])
        MerkleRoot_N_5,
        txlist_N_2,  # 第N-2个区块中包含的交易区块列表
    ):
        # 1：自己有的 2：需要向边缘节点请求的
        self.shard_id = shard_id  # 2
        self.shard_length = shard_length  # 2
        self.previous_hash = previous_hash  # 2
        self.txlist_N_2_hash = txlist_N_2_hash  # 2 edge挑选签名超过一定阈值的交易形成
        self.MerkleRoot_N_5 = MerkleRoot_N_5  # 2 存在edge_node.storage中
        self.txlist_N_2 = txlist_N_2  # 2 edge挑选签名超过一定阈值的交易形成
        self.timestamp = None  # 1
        self.vrf = None  # 1
        self.pk_pem = None  # 1
        self.sig = None
        # self.ConsensusSig = []

    def get_str(self):
        shard_data = str(self.shard_id) + str(self.shard_length)
        time_data = str(self.timestamp)
        data = shard_data + time_data
        return data.encode()

    def set_sig(self, sk):
        self.sig = signing(self.get_str(), sk)

    def set_publickey(self, public_key):
        self.pk_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def get_publickey(self):
        return serialization.load_pem_public_key(self.pk_pem,)


class TxBlock():
    def __init__(
        self,
        shard_id,
        shard_length,
        txs
    ):
        self.shard_id = shard_id
        self.shard_length = shard_length
        self.txs = txs
        self.timestamp = None
        self.sig = None
        self.pk_pem = None

    def get_str(self):
        shard_data = str(self.shard_id) + str(self.shard_length)
        time_data = str(self.timestamp)
        data = shard_data + time_data
        return data.encode()

    def set_sig(self, sk):
        self.sig = signing(self.get_str(), sk)

    def get_txs(self):
        return self.txs

    def set_publickey(self, public_key):
        self.pk_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    def get_publickey(self):
        return serialization.load_pem_public_key(self.pk_pem,)

    # def get_header_str(self):
    #     shard_data = str(self.shard_id) + str(self.shard_length)
    #     time_data = str(self.timestamp)
    #     tx_data = ""
    #     if self.merkle != None:
    #         tx_data = self.merkle
    #     data = shard_data + time_data + tx_data + str(self.nonce)
    #     return data

    # def combine_hash_data(self):
    #     data = self.get_header_str()
    #     return hashlib.sha256(data.encode("utf-8")).hexdigest()
