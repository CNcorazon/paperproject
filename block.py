"""
区块类
"""

from transaction import Tx
import hashlib
import random
import sys
import ecdsa


class ProBlock:
    def __init__(
        self,
        shard_id,  # 分片编号
        shard_length,  # 分片长度
        previous_hash,  # 第N-1个区块的哈希
        txlist_N_2_hash,  # 第N-2个区块中包含的交易区块列表哈希
        MerkleRoot_N_5,  # 第N-5个区块对应的merkleroot
        timestamp,  # 时间戳
        vrf,  # VRF
        publicKey,  # 出块人的公钥
        txlist_N_2,  # 第N-2个区块中包含的交易区块列表
    ):
        self.shard_id = shard_id
        self.shard_length = shard_length
        self.previous_hash = previous_hash
        self.txlist_N_2_hash = txlist_N_2_hash
        self.MerkleRoot_N_5 = MerkleRoot_N_5
        self.timestamp = timestamp
        self.vrf = vrf
        self.publicKey = publicKey
        self.txlist_N_2 = txlist_N_2
        self.sig = None

    def get_shard_id(self):
        return self.shard_id

    def get_vrf(self):
        return self.vrf

    def plus_nonce(self):
        self.nonce += 1
        return self.nonce

    def random_nonce(self):
        self.nonce = random.randint(0, 100000)
        return self.nonce

    def get_str(self):
        shard_data = str(self.shard_id) + str(self.shard_length)
        time_data = str(self.timestamp)
        data = shard_data + time_data + str(self.nonce)
        return data.encode()

    def set_public_key(self, sk):
        self.sig = sk.sign(self.get_str()).hex()

    def verify_block(self, public_key):
        vk = ecdsa.VerifyingKey.from_string(
            bytes.fromhex(public_key), curve=ecdsa.SECP256k1
        )
        try:
            if vk.verify(bytes.fromhex(self.sig), self.get_str()):
                return True
        except:
            return False


class ProBlock(Block):
    def __init__(
        self,
        shard_id,
        shard_length,
        previous_hash,
        timestamp,
        difficulty,
        nonce,
        validity_proof,
        txmerkle,
        txlinks,
    ):
        super(ProBlock, self).__init__(
            shard_id, shard_length, previous_hash, timestamp, difficulty, nonce
        )
        self.validity_proof = validity_proof
        self.txmerkle = txmerkle
        self.txlinks = txlinks

    def combine_hash_data(self):
        shard_data = str(self.shard_id) + str(self.shard_length)
        time_data = str(self.timestamp)
        tx_data = ""
        if self.txmerkle != None:
            tx_data = self.txmerkle
        data = shard_data + time_data + tx_data + str(self.nonce)
        return hashlib.sha256(data.encode("utf-8")).hexdigest()


class TxBlock(Block):
    def __init__(
        self,
        shard_id,
        shard_length,
        previous_hash,
        timestamp,
        difficulty,
        nonce,
        validity_proof,  # 有效性证明
        merkle,  # 交易的Merkle树根(使用merkletools)
        txs,  # 交易
        links,  # 其他区块的链接
    ):
        super(TxBlock, self).__init__(
            shard_id, shard_length, previous_hash, timestamp, difficulty, nonce
        )
        self.validity_proof = validity_proof
        self.merkle = merkle
        self.txs = txs
        self.links = links

    def get_header_str(self):
        shard_data = str(self.shard_id) + str(self.shard_length)
        time_data = str(self.timestamp)
        tx_data = ""
        if self.merkle != None:
            tx_data = self.merkle
        data = shard_data + time_data + tx_data + str(self.nonce)
        return data

    def combine_hash_data(self):
        data = self.get_header_str()
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def get_txs(self):
        return self.txs


class VoteBlock(Block):
    def __init__(
        self,
        shard_id,
        shard_length,
        previous_hash,
        timestamp,
        difficulty,
        nonce,
        txblock_hash,  # 交易区块的哈希
    ):
        super(VoteBlock, self).__init__(
            shard_id, shard_length, previous_hash, timestamp, difficulty, nonce
        )
        self.txblock_hash = txblock_hash

    def combine_hash_data(self):
        shard_data = str(self.shard_id) + str(self.shard_length)
        time_data = str(self.timestamp)
        data = shard_data + time_data + str(self.nonce)
        return hashlib.sha256(data.encode("utf-8")).hexdigest()
