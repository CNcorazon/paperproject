'''
移动节点，只保存N和list（shuffle的话需要每一个块更新一次，先做个静态的）
'''

from merkletools import MerkleTools
from mobile_communicator import Communicator
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


class MobileNodeStorage():
    def __init__(self, node_ip, shard_id, nodes, shard_num):
        self.node_ip = node_ip
        self.shard_id = shard_id
        self.nodes = nodes
        self.shard_num = shard_num
        self.node_num = 4
        self.N = 0
        self.public_keys = {}

        self.weight = 0
        self.totalweight = 0

        self.previous_hash = '0'
        self.gs_root = b''

        self.txs = {}

        self.pi = b'0'
        self.votes = 0

        # 有MAXSTEP个列表
        self.votelist = [[], [], [], [], [], [], [], [], [], []]

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


class MobileNode():
    def __init__(self, node_ip, shard_id, nodes, shard_num):
        # 节点存储
        self.node_storage = MobileNodeStorage(
            node_ip, shard_id, nodes, shard_num)
        self.communicator = Communicator(shard_num)
        self.shard_id = shard_id
        # 私钥
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend())

        self.public_key = self.private_key.public_key()

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

    '''
    通信模块，分为发送和接受
    '''

    def send_msg(self, ip):
        msg = self.SendMsgBuffer.pop()
        self.communicator.send_msg(msg, ip)

    def recv_msg(self, ip):
        self.communicator.recv_msg(self.RecvMsgBuffer, ip)

    def recv_problockmsg(self, ip):
        self.communicator.recv_problock_msg(self.ProBlockMsgBuffer, ip)

    def recv_txblockmsg(self, ip):
        self.communicator.recv_txblock_msg(self.TxBlockBuffer, ip)

    def recv_teeproof(self, ip):
        self.communicator.recv_TeeProof_msg(self.TeeProofBuffer, ip)
    '''
    计算vrf,并提出pro_block
    '''

    def propose_block(self):
        msg, priority = self.ProBlockMsgBuffer.pop()
        pro_block = msg.sign_msg
        print('shard_id:', pro_block.shard_id)
        seed = str(pro_block.shard_length) + pro_block.previous_hash
        # sortition.Sortiiton(self.private_key, seed, config.CANDIDATE,
        #                     self.node_storage.weight, self.node_storage.totalweight)
        # 简略实现
        pi = rsa_vrf.get_vrf(seed, self.private_key)
        votes = bin(int(binascii.hexlify(pi), 16))[-2:]
        # 1/4的概率提出problock
        print(votes)
        if votes == '00' or votes == '01' or votes == '10' or votes == '11':
            # 补充problock中的信息，block.py中的 #1部分
            pro_block.timestamp = int(time.time())
            pro_block.vrf = self.node_storage.pi
            pro_block.set_publickey(self.public_key)
            pro_block.set_sig(self.private_key)
            # 放进message类中
            sig = signing(pro_block.get_str(), self.private_key)
            msg1 = message(self.public_key, sig, 'pro_block', pro_block)
            self.SendMsgBuffer.push(msg1, random.randint(2, 10000))

    '''
    BA* 共识模块
    '''

    def Reduction(self):
        # 该步骤的目的是将consensus on arbitrary value转化为consensus on binary value, i.e. {block_hash, empty_hash}
        # 从candidate中选出vrf最小的作为自己本地的胜者，检查proposal block中的交易是否有超过2/3的签名，检查global root的签名是否超过2/3
        msg, priority = self.RecvMsgBuffer.pop()
        pro_block = msg.sign_msg
        winner = pro_block
        tmp = int(binascii.hexlify(pro_block.vrf), 16)
        while pro_block != 'timeout':
            msg, priority = self.RecvMsgBuffer.threshold_pop()
            pro_block = msg.sign_msg
            if pro_block != 'timeout' and int(binascii.hexlify(pro_block.vrf), 16) < tmp:
                winner = pro_block

        # 首先验证block的签名
        verification(winner.publicKey, winner.sig, winner.get_str())
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
        value = hashlib.sha256(winner.get_str()).hexdigest()
        sig = signing(value, self.private_key)
        msg = message(self.public_key, sig, 'consensus_reduction', value)
        self.SendMsgBuffer.push(msg, 1)
        hblock = self.CountVote(0, config.EXPIRED_THRESHOLD)
        return hblock

    def CommitteeVote(self, _step, value):
        # flag == 0, countvote, flag == 1, no countvote
        # step == 0, reduction, else, binaryBA
        # ⟨pk,signed_m⟩ ← msg
        # ⟨round,step,π,hprev,value⟩ ← signed_m
        pk = self.public_key
        sk = self.private_key
        hprev = self.node_storage.previous_hash
        pi = self.node_storage.pi
        weight = self.node_storage.weight
        totalweight = self.node_storage.totalweight
        _round = self.node_storage.N + 1
        sign_m = {'round': _round, 'step': _step, 'pi': pi,
                  'hprev': hprev, 'value': value, 'weight': weight, 'totalweight': totalweight}
        sig = signing(pickle.dumps(sign_m), sk)
        msg = message(public_key=pk, sig=sig,
                      msgtype='consensus', sign_msg=sign_m)
        # 随机生成priority
        self.SendMsgBuffer.push(msg, random.randint(2, 10000))

    def CountVote(self, step, threshold):
        counts = {}
        voters = []
        # 这边用了两个timeout，原因是没有找到合适的方法去按照round和step表示incomingMsgs[round,step]
        start = time.time()
        if step == 0:
            while True:
                m = self.RecMsgBuffer.threshold_pop(threshold)
                if m == None:
                    print('timeout!')
                    return 'timeout'
                value = m.sign_msg
                # 目前所有的投票均使用一人一票
                votes = 1
                if not value in counts.keys():
                    counts[value] = votes
                    # print(counts)
                else:
                    counts[value] = counts[value] + votes
                count_ = sorted(counts.items(), key=lambda kv: (
                    kv[1], kv[0]), reverse=True)
                if count_[0][1] > 2/3 * self.node_storage.node_num():
                    return count_[0][0]
        else:
            while True:
                m = self.RecMsgBuffer.threshold_pop(threshold)
                if m == None:
                    print('timeout!')
                    return 'timeout'
                #  这一步是保证取出的msg是正确的round和step，若不是，则重新赋一个随机prority,push进去。
                if m[0].sign_msg['round'] != self.node_storage.N or m[0].sign_msg['step'] != step:
                    self.RecMsgBuffer.push(m[0], random.randint(2, 10000))
                    if time.time() > start + threshold:
                        return 'timeout'
                    continue
                votes, value = self.ProcessMsg(m[0])
                if (m[0].pk_pem in voters) or votes == 0:
                    continue
                voters.append(m[0].pk_pem)
                # print(value)
                if not value in counts:
                    counts[value] = votes
                    # print(counts)
                else:
                    counts[value] = counts[value] + votes
                count_ = sorted(counts.items(), key=lambda kv: (
                    kv[1], kv[0]), reverse=True)
                start = time.time()
                # 当收到的投票大于阈值之后，返回hblock
                print(count_)
                if count_[0][1] > 2/3 * self.node_storage.node_num():
                    return count_[0][0]


#  sign_m = {'round': _round, 'step': _step, 'pi': pi,
#                   'hprev': hprev(string), 'value': value(string), 'weight': weight, 'totalweight': totalweight}

    def ProcessMsg(self, msg):
        pk = serialization.load_pem_public_key(msg.pk_pem)
        sig = msg.sig
        sign_msg = msg.sign_msg
        if not verification(pk, sig, pickle.dumps(sign_msg)):
            return 0, 0
        _round = sign_msg['round']
        _step = sign_msg['step']
        pi = sign_msg['pi']
        hprev = sign_msg['hprev']
        value = sign_msg['value']
        weight = sign_msg['weight']
        totalweight = sign_msg['totalweight']
        seed = str(_round) + hprev
        if hprev != self.node_storage.previous_hash:
            return 0, 0
        votes = sortition.VerifySort(
            pk, pi, seed, config.CANDIDATE, weight, totalweight)
        return votes, value

    def BinaryBA(self, block_hash):
        # '00' means TIMEOUT '0'means emptyhash
        time.sleep(6)
        step = 1
        r = block_hash
        while step < config.MAXSTEP:
            self.CommitteeVote(step, r)
            r = self.CountVote(step, config.EXPIRED_THRESHOLD)
            if r == 'timeout':
                r = block_hash
            elif r != 'empty_block':
                self.CommitteeVote(step+1, r)
                self.CommitteeVote(step+2, r)
                self.CommitteeVote(step+3, r)
                if step == 1:
                    self.CommitteeVote(config.FINAL, r)
                return r
            step = step + 1

            self.CommitteeVote(step, r)
            r = self.CountVote(step, config.EXPIRED_THRESHOLD)
            if r == 'timeout':
                r = 'empty_block'
            elif r == 'empty_block':
                self.CommitteeVote(step+1, r)
                self.CommitteeVote(step+2, r)
                self.CommitteeVote(step+3, r)
                return r
            step = step + 1

            self.CommitteeVote(step, r)
            r = self.CountVote(step, config.EXPIRED_THRESHOLD)
            if r == 'timeout':
                if CommonCoin() == 0:
                    r = block_hash
                else:
                    r = 'empty_block'
            step = step + 1

    def BAstar(self):
        hblock = self.Reduction()
        hblock_star = self.BinaryBA(hblock)
        # 检查是fianl/tentative共识,1:final,0:tentative
        r = self.CountVote(config.FINAL, config.EXPIRED_THRESHOLD_FINAL)
        if hblock_star == r:
            msg = message(public_key=self.public_key, sig=signing(pickle.dumps({'consensus_block': hblock_star, 'votes': self.node_storage.votes}), self.private_key),
                          msgtype='final_consensus', sign_msg={'consensus_block': hblock_star, 'votes': self.node_storage.votes})
            self.SendMsgBuffer.push(msg, 1)
            return 'FINAL', hblock_star
        else:
            msg = message(public_key=self.public_key, sig=signing(pickle.dumps({'consensus_block': hblock_star, 'votes': self.node_storage.votes}), self.private_key),
                          msgtype='tentative_consensus', sign_msg={'consensus_block': hblock_star, 'votes': self.node_storage.votes})
            self.SendMsgBuffer.push(msg, 1)
            return 'TENTATIVE', hblock_star

    '''
    交易块签名模块
    '''

    def signing_txblock(self):
        msg, priority = self.TxBlockBuffer.pop()
        txblock = msg.sign_msg
        txblock.timestamp = int(time.time())
        txblock.publicKey = self.public_key
        txblock.set_sig(self.private_key)
        txblock_sig = message(public_key=self.public_key, sig=signing(pickle.dumps(
            txblock), self.private_key), msgtype='txblock_sig', sign_msg=txblock)
        self.SendMsgBuffer.push(txblock_sig, random.randint(2, 10000))
    '''
    交易验证模块（tee有效性证明的签名
    '''

    def signing_teeproof(self):
        # 该步骤需要验证不同tee的proof
        msg, priority = self.TeeProofBuffer.pop()
        teepk = serialization.load_pem_public_key(msg.public_key)
        if verification(public_key=teepk, sig=msg.sig, msg=msg.sign_msg):
            sig = message(public_key=self.public_key, sig=signing(pickle.dumps(
                msg.sign_msg), self.private_key), msgtype='proof_sig', sign_msg=msg.sign_msg)
            self.SendMsgBuffer.push(sig, random.randint(2, 10000))

    def main():
        return 0


if __name__ == '__main__':
    serverip = '192.168.199.104'
    serverip1 = '10.211.55.4'

    node = MobileNode('192.168.199.104', 1, 2, 1)
    node1 = MobileNode('192.168.199.104', 1, 2, 1)
    node2 = MobileNode('192.168.199.104', 1, 2, 1)
    node3 = MobileNode('192.168.199.104', 1, 2, 1)
    node.node_storage.set_N(5)
    node1.node_storage.set_N(5)
    node2.node_storage.set_N(5)
    node3.node_storage.set_N(5)

    problock = ProBlock(1, 1, b'0', b'0', [], time.time(),
                        node.node_storage.pi, node.public_key, [])
    problock.set_sig(node.private_key)

    flag, hblock_star = node.BAstar(problock, serverip)

    print(flag, hblock_star)

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

    # def proposer_selection(self, shard_id, node_ip):
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
    #         self.communicator.send_vrf(shard_id, node_ip, pi, com, signature)

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
