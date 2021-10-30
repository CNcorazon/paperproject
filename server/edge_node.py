'''
边缘节点，保存global state和区块链
'''


from queue import Queue
from block import ProBlock, TxBlock
from message import message
from util import PriorityQueue
# from merkletools import MerkleTools
# from mpt import MerklePatriciaTrie
from edge_communicator import Communicator
# from block import Block
import hashlib
import time
import random
import zmq
import config
import sortition
import pickle
from rsa_sign import *
from cryptography.hazmat.primitives import serialization

# 线程：接受交易发起者的local proof请求；接受交易发起者的交易；

# 只设置一个边缘节点，暂时不考虑边缘节点之间的gossip


# # 一个分片的存储
class EdgeNodeStorage():
    def __init__(self, shard_id):
        self.shard_id = shard_id
        self.weightlist = {}
        self.totalweight = 0
        self.mobilenodelist = []

        self.proposal_block = []
        self.transaction_block = []
        self.transaction_block_pool = []

        for _ in range(config.MAXLENGTH):
            self.transaction_block_pool.append([])

        for _ in range(config.MAXLENGTH):
            self.transaction_block.append([])

        for _ in range(config.SHARD_NUM):
            self.proposal_block.append([])

    def update_mobilelist(self, pk_pem):
        self.mobilenodelist.append(pk_pem)
        # 初始化权重
        self.weightlist[msg.pk_pem] = 10
        self.totalweight = self.totalweight + 10

    def get_mobileweight(self, pk_pem):
        return self.weightlist[pk_pem]


class EdgeNode():
    def __init__(self, shard_id):
        self.shard_id = shard_id
        # 私钥
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend())

        self.public_key = self.private_key.public_key()

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

        self.communicator = Communicator(shard_id)
        self.node_storage = EdgeNodeStorage(shard_id)

    def recvmsgs(self):
        self.communicator.recv_msg(self.RecMsgBuffer)

    def sendgossipmsg(self):
        msg = self.SysnMsgBuffer.pop()
        ip_list = ['172.20.10.3']
        for ip in ip_list:
            self.communicator.send_gossipvote(msg, ip)

    def sendmsgs(self):
        msg = self.SendMsgBuffer.pop()
        msg[0].update(self.node_storage.get_mobileweight(
            msg[0].pk_pem), self.node_storage.totalweight)
        self.communicator.send_msg(msg)

    def sendproblock(self):
        msg = self.ProBlockMsgBuffer.pop()
        self.communicator.send_problockmsg(msg)

    def sendtxblock(self):
        msg = self.TxBlockMsgBuffer.pop()
        self.communicator.send_txblockmsg(msg)

    def sendteeproof(self):
        msg = self.TeeProofMsgBuffer.pop()
        self.communicator.send_teeproof(msg)
    # 从消息buffer中读取消息，分流到不同的处理模块

    def message_forwarding(self):
        # BA*共识投票，最终的共识结果，对交易块的签名，对有效性证明的验证签名
        # msg = (item, priority)
        msg = self.RecMsgBuffer.pop()
        if msg[0].togossip == True:
            msg[0].togossip = False
            self.SysnMsgBuffer.push(msg[0], msg[1])
        # 前三个是只需要经过服务器gossip的信息
        if msg.type == 'pro_block':
            self.SendMsgBuffer.push(msg[0], msg[1])
        elif msg.type == 'reduction':
            self.SendMsgBuffer.push(msg[0], msg[1])
        elif msg.type == 'consensus':
            self.SendMsgBuffer.push(msg[0], msg[1])
        # 后三个是服务器需要处理和存储的信息
        elif msg.type == 'final_consensus':
            self.AppendBlockSigBuffer.push(msg[0], msg[1])
        elif msg.type == 'txblock_sig':
            self.TxBlockSigBuffer.push(msg[0], msg[1])
        elif msg.type == 'proof_sig':
            self.TeeProofSigBuffer.push(msg[0], msg[1])
        else:
            print('wrong msg')

    def init_buffer(self):
        self.AppendBlockSigBuffer = PriorityQueue()
        self.TxBlockSigBuffer = PriorityQueue()
        self.TeeProofSigBuffer = PriorityQueue()
        self.TxBlockMsgBuffer = PriorityQueue()
        self.TeeProogMsgBuffer = PriorityQueue()

    '''
    新块上链，清空每个模块的buffer；
    n-1个块进入交易验证（之前是在给交易区块签名，当problock上链之后，
    服务器不再发送交易区块，但还是会有残余的交易区块签名被移动区块上传
    处理方式：服务器去检查一下txsig是不是对最新的problock上的tx的签名）；
    n进行交易块签名（提交完consensus结果之后就等待服务器发送txblock）；
    n+1开始进行共识（就是说可以先准备好vrf，等待problock_candidate）
    '''

    '''
    三个阶段各一个线程
    '''

    def generate_problock(self):
        # 花三秒时间来创建problock, 省略对n-2块和n-5个块签名的确认
        time.sleep(3)
        block = ProBlock(1, len(
            self.node_storage.proposal_block[1])+1, self.node_storage.proposal_block[1][-1], None, None, None)
        return block

    def AppendBlock(self):
        counts = 0
        pro_block = ProBlock(1, len(
            self.node_storage.proposal_block[1])+1, '0', None, None, None)
        pro_block_msg = message(public_key=self.public_key, sig=signing(
            pickle.dumps(pro_block), self.private_key), msgtype='Problock', sign_msg=pro_block)
        self.ProBlockMsgBuffer.push(
            pro_block_msg, random.randint(2, 10000))
        while True:
            # 暂不记录投票人的信息，只要投票数够了就上链
            msg = self.AppendBlockSigBuffer.pop()
            votes = msg[0].sign_msg['votes']
            counts = counts + votes
            if counts > 2/3*config.NODE_NUM:
                self.node_storage.proposal_block[self.shard_id].append(
                    msg[0].sign_msg['consensus_block'])
                # 清空所有buffer（除了同步buffer），确保不再发送消息（但是要处理移动节点超时上传的msg
                self.init_buffer()
                # 发送problock
                pro_block = self.generate_problock()
                pro_block_msg = message(public_key=self.public_key, sig=signing(
                    pickle.dumps(pro_block), self.private_key), msgtype='Problock', sign_msg=pro_block)
                self.ProBlockMsgBuffer.push(
                    pro_block_msg, random.randint(2, 10000))

    def generate_txblock(self):
        # 花0.5秒来创建txblock, 省略打包步骤
        time.sleep(0.5)
        tx_block = TxBlock(
            1, len(self.node_storage.proposal_block[1]), None)
        tx_block_msg = message(public_key=self.public_key, sig=signing(
            pickle.dumps(tx_block), self.private_key), msgtype='Txblock', sign_msg=tx_block)
        self.TxBlockMsgBuffer.push(tx_block_msg, random.randint(2, 10000))

    def CollectTxblock(self):
        txblock, priority = self.TxBlockSigBuffer.pop()
        # 根据timestamp进行排序
        self.node_storage.transaction_block_pool[len(
            self.node_storage.proposal_block[self.shard_id])].append(txblock)
        self.node_storage.transaction_block_pool[len(self.node_storage.proposal_block[self.shard_id])] = sorted(
            self.node_storage.transaction_block_pool[len(self.node_storage.proposal_block[self.shard_id])], key=lambda x: x.timestamp)

    def tx_validation(self):
        # 单个txblock的验证时间为
        problock_num = len(self.node_storage.proposal_block[self.shard_id]) - 3
        count = 1
        if problock_num > 0:
            for txblock in self.node_storage.transaction_block_pool[len(self.node_storage.proposal_block[self.shard_id])]:
                time.sleep(2)
                print("validation processing")
                # msg中可以模拟验证的成功率，比如生成一个1-100随机数，1-5则验证失败
                num = random.randint(1, 100)
                # if num > 5:
                #     merkleroot = 'NewMerkleRoot'
                # else:
                #     merkleroot = 'OldMerkleRoot'
                merkleroot = 'NewMerkleRoot'
                sign_msg = {'num': num, 'merkleroot': merkleroot,
                            'problock_num': problock_num, 'txblock_num': count}
                proof = message(public_key=public_key, sig=signing(
                    pickle.dumps(sign_msg), self.private_key), msgtype='Teeproof', sign_msg=sign_msg)
                proof.togossip = False
                self.SysnMsgBuffer.push(proof, random.randint)
                self.TeeProogMsgBuffer.push(proof, random.randint(2, 10000))
                print('tee待验证交易块数量:', len(
                    self.node_storage.transaction_block_pool[len(self.node_storage.proposal_block[self.shard_id])] - count))

    def AppendTxblock(self):
        # 需要由不同tee签名的txblock才可以上链
        msg, priority = self.TeeProofSigBuffer.pop()
        count = {}
        if not str(msg.sign_msg['block_num']) in count.keys():
            count[str(msg.sign_msg['block_num'])] = 1
        else:
            count[str(msg.sign_msg['block_num'])] = count[str(
                msg.sign_msg['block_num'])] + 1
        for key in count:
            if count[key] > 2/3 * config.TEE_NUM:
                del count[key]
                self.node_storage.transaction_block[len(
                    self.node_storage.proposal_block[self.shard_id])].append(key)
