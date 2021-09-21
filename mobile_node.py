'''
移动节点，只保存N和list（shuffle的话需要每一个块更新一次，先做个静态的）
'''

from os import pipe
from queue import Empty, Queue
from merkletools import MerkleTools
from mobile_communicator import Communicator
# import ecdsa
import config
import hashlib
import rsa_vrf
import binascii
import time
from CommonCoin import CommonCoin
from block import ProBlock
from rsa_sign import *
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization


class MobileNodeStorage():
    def __init__(self, node_id, shard_id, nodes, shard_num):
        self.node_id = node_id
        self.shard_id = shard_id
        self.nodes = nodes
        self.shard_num = shard_num
        self.node_num = 0
        self.N = 0
        self.public_keys = {}

        self.previous_hash = 0
        self.gs_root = b''

        self.txs = {}

        self.pi = b'0'

    def get_N(self):
        return self.N

    def set_N(self, num):
        self.N = num

    def update_list(self, public_key_list):
        self.public_keys = public_key_list

    def get_previous_hash(self):
        return self.previous_hash

    def set_previous_hash(self, shard_id, previous_hash):
        self.previous_hash = previous_hash

    def get_pi(self):
        return self.pi

    def set_pi(self, pi):
        self.pi = pi

    def get_gs_root(self):
        return self.gs_root

    def set_gs_root(self, root):
        self.gs_root = root

    def get_node_num(self):
        return self.node_num

    def set_node_num(self, num):
        self.node_num = num


class MobileNode():
    def __init__(self, node_id, shard_id, nodes, shard_num):
        # 节点存储
        self.node_storage = MobileNodeStorage(
            node_id, shard_id, nodes, shard_num)
        self.communicator = Communicator(shard_num)

        # 私钥
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend())

        self.shard_id = shard_id

    def Reduction(self, pro_block, ip):
        # 该步骤的目的是将consensus on arbitrary value转化为consensus on binary value, i.e. {block_hash, empty_hash}
        # 从candidate中选出vrf最小的作为自己本地的胜者，检查proposal block中的交易是否有超过2/3的签名，检查global root的签名是否超过2/3
        # candidate [[vrf,pk,block],[vrf,pk,block]]

        #local_winner = min(candidate)
        # pk = local_winner[0]
        # pro_block = local_winner[1]

        # 首先验证block的签名
        pk = read_public_key()
        verification(pk, pro_block.sig, pro_block.get_str())
        # # 验证交易是否超过2/3的签名
        # for tx in pro_block.txlist_N_2:
        #     for sig in tx.witness_sig:
        #         if verification(sig[0], sig[1], tx):
        #             count = count + 1
        #         if count > 2/3 * self.node_storage.get_node_num:
        #             print('witness sig check!')
        #             break
        # # 检验global state是否超过2/3的签名
        # for sig in pro_block.MerkleRoot_N_5[2:]:
        #     verification(sig[0], sig[1], pro_block.MerkleRoot_N_5[0])
        #     count1 = count1 + 1
        #     if count1 > 2/3 * self.node_storage.get_node_num():
        #         print('global state sig check!')
        #         break
        # 投票
        value = hashlib.sha256(pro_block.get_str()).hexdigest()
        self.CommitteeVote(ip, 0, value, 0)
        # if count > 2/3 * self.node_storage.get_node_num() and count1 > 2/3 * self.node_storage.get_node_num():
        #     # pro_block.get_str()中没有用encode("utf-8") 不知道有没有bug
        #     value = hashes.SHA256(pro_block.get_str()).hexdigest()
        #     self.CommitteeVote(self.node_storage.N + 1, 0, value)
        # else:
        #     # 发送empty_hash
        #     value = b'0'
        #     self.CommitteeVote(self.node_storage.N + 1, 0, value)

    def CommitteeVote(self, ip, _step, value, flag):
        # flag == 0, countvote, flag == 1, no countvote
        # step == 0, reduction, else, binaryBA
        # ⟨pk,signed_m⟩ ← msg
        # ⟨round,step,π,hprev,value⟩ ← signed_m
        pk = self.node_storage.node_id
        hprev = self.node_storage.get_previous_hash()
        pi = self.node_storage.get_pi()
        _round = self.node_storage.N + 1
        sign_m = str(_round) + str(' ') + str(_step) + str(' ') + \
            str(pi) + str(' ') + str(hprev) + str(' ') + str(value)
        sign_m = sign_m.encode()
        msg = [pk, sign_m]
        self.communicator.send_vote(msg, ip)
        if flag == 0:
            hblock = self.CountVote(ip)
            print(hblock)
        else:
            while True:
                print('21')
                pem, sig, msg = self.communicator.recv_vote(ip)
                # 存入storage
                if pem == b'0':
                    print('CommitteeVote end')
                    break

    def CountVote(self, ip):
        test = 0
        counts = {}
        voters = []
        while True:
            pem, sig, msg = self.communicator.recv_vote(ip)
            if pem == b'0':
                print('Time out!')
                return b'0'
            # counts 按照value降序排列

            votes, value = self.ProcessMsg(pem, sig, msg)
            # if (pem in voters) or votes == 0:
            #    continue
            voters.append(pem)
            print(value)
            if not value.decode() in counts:
                print('---------------785431---------------')
                counts[value.decode()] = votes
                print(counts)
            else:
                print('---------------121231---------------')
                counts[value.decode()] = counts[value.decode()] + votes
            count_ = sorted(counts.items(), key=lambda kv: (
                kv[1], kv[0]), reverse=True)
            # 当收到的投票大于阈值之后，返回hblock
            print(count_)
            if count_[0][1] > 2:
                return count_[0][1]

    def ProcessMsg(self, pem, sig, msg):
        pk = serialization.load_pem_public_key(pem)
        verification(pk, sig, msg)
        votes = 1
        value = b'1'
        return votes, value

    def BinaryBA(self, block_hash, ip):
        # b'00' means TIMEOUT b'0'means emptyhash
        step = 1
        r = block_hash
        empty_hash = b'0'
        timeout = b'00'
        while step < config.MAXSTEP:
            r = self.CommitteeVote(ip, step, r, 0)
            if r == timeout:
                r = block_hash
            elif r != empty_hash:
                self.CommitteeVote(ip, step+1, r, 1)
                self.CommitteeVote(ip, step+2, r, 1)
                self.CommitteeVote(ip, step+3, r, 1)
                if step == 1:
                    self.CommitteeVote(ip, config.FINAL, r, 1)
                return r
            step = step + 1

            r = self.CommitteeVote(ip, step, r, 0)
            if r == timeout:
                r = empty_hash
            elif r == empty_hash:
                self.CommitteeVote(ip, step+1, r, 1)
                self.CommitteeVote(ip, step+2, r, 1)
                self.CommitteeVote(ip, step+3, r, 1)
                return r
            step = step + 1

            r = self.CommitteeVote(ip, step, r, 0)
            if r == timeout:
                if CommonCoin() == 0:
                    r = block_hash
                else:
                    r = empty_hash
            step = step + 1


if __name__ == '__main__':
    node = MobileNode('192.168.199.105', 1, 2, 1)
    storage = MobileNodeStorage('192.168.199.105', 1, 2, 1)
    storage.set_N(5)
    problock = ProBlock(1, 1, b'0', b'0', [], time.time(),
                        node.node_storage.pi, node.node_storage.node_id, [])
    problock.set_sig(read_private_key())
    serverip = '192.168.199.105'
    node.Reduction(problock, serverip)

# def send_public_key(self):
    #     public_key = self.private_key.public_key()
    #     self.communicator.send_key(public_key, self.node_storage.nodes)

    # def recv_public_key(self):
    #     public_key, addr = self.communicator.recv_key()
    #     public_key = public_key.hex()
    #     return public_key, addr

    # def recv_block_N(self, shard_id):
    #     # 从服务器获得最新的层数
    #     N = self.communicator.recv_N(shard_id)
    #     self.node_storage.set_N(N)
    #     return N

    # def recv_previous_hash(self, shard_id):
    #     # 从服务器获得最新块的哈希
    #     previous_hash = self.communicator.recv_previous_hash(shard_id)
    #     self.node_storage.set_previous_hash(shard_id, previous_hash)

    # def proposer_selection(self, shard_id, node_id):
    #     # 若自己是proposer，下载com，并且将com和自己的vrf发送给服务器
    #     # proposer_check()
    #     pi = self.get_vrf(shard_id)
    #     pii = binascii.hexlify(pi)
    #     vrf = bin(int(pii, 16))
    #     if int(vrf[-config.VRF_THRESHOLD:], 2) == 0:
    #         com = self.communicator.recv_txdigest(shard_id)
    #         # pi, com, signiture on hash(com)
    #         signature = self.private_key.sign(
    #             com,
    #             padding.PSS(
    #                 mgf=padding.MGF1(hashes.SHA256()),
    #                 salt_length=padding.PSS.MAX_LENGTH
    #             ),
    #             hashes.SHA256()
    #         )
    #         self.communicator.send_vrf(shard_id, node_id, pi, com, signature)

    # def winner_selection(self, shard_id):
    #     # 共识期间，每个委员会成员读取proposers的VRF，选出最低VRF proposer作为出块者，投他一票
    #     vrf_list = self.communicator.recv_pro_vrf(shard_id)
    #     winner_vrf = min(vrf_list)
    #     winner_id = 0
    #     self.communicator.send_vote(shard_id, winner_id)

    # def get_txs_from_edge(self, shard_id, com):
    #     t = self.communicator.recv_tx(shard_id)

    # def clean_txs(self):
    #     return None

    # def verify_tx(self, shard_id):
    #     # 验证winner的块里的交易
    #     for i in self.node_storage.txs:
    #         self.communicator.recv_proof(shard_id, i)
    #     new_gs_root = b''
    #     return new_gs_root

    # def get_vrf(self, shard_id):
    #     N = self.node_storage.get_N()
    #     previous_hash = self.node_storage.get_previous_hash()
    #     data = str(N) + str(previous_hash)
    #     alpha = hashlib.sha256(data.encode('utf-8')).hexdigest()
    #     alpha = " ".join(alpha[1:])
    #     pi = rsa_vrf.get_vrf(alpha, self.private_key)
    #     return pi

    # def BA(self, shard_id):
    #     # two-step reduction
    #     # 1.由服务器端统计，得票最多的作为出块者，没有超过一定的阈值，则出空块
    #     # 2.服务器将出块者和区块广播给移动节点进行第二轮投票，若没有超过一定的阈值，也出空块
    #     # 最终可以确定，这一轮出empty block或者是proposal block
    #     # 第一轮
    #     self.winner_selection(shard_id)
    #     hblock_flag = self.communicator.recv_count_result(
    #         shard_id, self.node_storage.get_N())
    #     # binaryBA共识过程略去。。。
    #     if hblock_flag == 0:
    #         # append Empty(round,H(ctx.last_block)）
    #         self.clean_txs()
    #         com = []
    #         gs_root = self.node_storage.get_gs_root
    #         msg = gs_root + bin(self.node_storage.get_N()+1)
    #         signature = self.private_key.sign(
    #             msg,
    #             padding.PSS(
    #                 mgf=padding.MGF1(hashes.SHA256()),
    #                 salt_length=padding.PSS.MAX_LENGTH
    #             ),
    #             hashes.SHA256()
    #         )
    #         empty_block_info = [shard_id, self.node_storage.get_N+1,
    #                             self.node_storage.get_previous_hash(), time.time(), com, gs_root, signature]
    #         self.communicator.send_block(shard_id, empty_block_info)
    #     else:
    #         # append proposal block
    #         self.clean_txs()
    #         winner_info = self.communicator.recv_winner_info(shard_id)
    #         self.get_txs_from_edge(shard_id, winner_info[3])
    #         new_gs_root = self.verify_tx(shard_id)
    #         msg = new_gs_root + bin(self.node_storage.get_N()+1)
    #         signature = self.private_key.sign(
    #             msg,
    #             padding.PSS(
    #                 mgf=padding.MGF1(hashes.SHA256()),
    #                 salt_length=padding.PSS.MAX_LENGTH
    #             ),
    #             hashes.SHA256()
    #         )
    #         proposal_block_info = [shard_id, self.node_storage.get_N + 1,
    #                                self.node_storage.get_previous_hash, time.time(), winner_info[3], new_gs_root, signature]
    #         self.communicator.send_block(shard_id, proposal_block_info)

    # def polling4cst(self):
    #     # 一个线程：向边缘节点请求最新状态：N和GS，若和自己本地的不一样，则检查签名，签名正确则更新本地的N为N+1，GS为new_GS
    #     # gs_root[0]为根节点gs_root[1]为多方签名
    #     while True:
    #         print("------polling for newest state------")
    #         N = self.communicator.recv_N(self.shard_id)
    #         gs_root = self.communicator.recv_gs_root(self.shard_id)
    #         previous_hash = self.communicator.recv_previous_hash(self.shard_id)
    #         if N == self.node_storage.get_N()+1 and gs_root != self.node_storage.get_gs_root:
    #             if self.verifying_gs_signature(gs_root):
    #                 self.node_storage.set_N(N)
    #                 self.node_storage.set_gs_root(gs_root)
    #                 self.node_storage.set_previous_hash(
    #                     self.shard_id, previous_hash)
    #         time.sleep(60)

    # def verifying_gs_signature(self, root):
    #     # 应该是需要验证gsroot上committee的多方签名的，但是我不会！所以直接向服务器请求已经收到签名的个数（放在root[1]），达到了阈值就返回True
    #     if root[1] > config.GS_THRESHOLD:
    #         return True
    #     else:
    #         return False
