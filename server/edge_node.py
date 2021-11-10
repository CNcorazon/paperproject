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
import logging
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
        self.weightlist[pk_pem] = 10
        self.totalweight = self.totalweight + 10

    def get_mobileweight(self, pk_pem):
        if not pk_pem in self.weightlist.keys():
            self.update_mobilelist(pk_pem)
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

        self.iplist = ['172.20.10.3']
        self.communicator = Communicator(shard_id, self.iplist)
        self.node_storage = EdgeNodeStorage(shard_id)

        self.TxblockflagBuffer = PriorityQueue()

    def recvmsgs(self):
        self.communicator.recv_msg()

    def sendgossipmsg(self):
        while self.communicator.SysnMsgBuffer.getLength() <= 0:
            continue
        msg = self.communicator.SysnMsgBuffer.pop()
        self.communicator.send_gossipvote(msg)

    def sendmsgs(self):
        while self.communicator.SendMsgBuffer.getLength() <= 0:
            continue
        msg = self.communicator.SendMsgBuffer.pop()
        # msg[0].update_weight(self.node_storage.get_mobileweight(
        #     msg[0].pk_pem), self.node_storage.totalweight)
        self.communicator.send_msg(msg)

    def sendproblock(self):
        while self.communicator.ProBlockMsgBuffer.getLength() <= 0:
            continue
        msg = self.communicator.ProBlockMsgBuffer.pop()
        print('send了但没有完全send:', msg)
        self.communicator.send_problockmsg(msg)

    def sendtxblock(self):
        while self.communicator.TxBlockMsgBuffer.getLength() <= 0:
            continue
        msg = self.communicator.TxBlockMsgBuffer.pop()
        self.communicator.send_txblockmsg(msg)

    def sendteeproof(self):
        while self.communicator.TeeProofMsgBuffer.getLength() <= 0:
            continue
        msg = self.communicator.TeeProofMsgBuffer.pop()
        self.communicator.send_teeproofmsg(msg)
    # 从消息buffer中读取消息，分流到不同的处理模块

    def message_forwarding(self):
        # BA*共识投票，最终的共识结果，对交易块的签名，对有效性证明的验证签名
        # msg = (item, priority)
        while self.communicator.RecMsgBuffer.getLength() <= 0:
            continue
        msg = self.communicator.RecMsgBuffer.pop()
        if msg[1] != 0:
            # 前三个是只需要经过服务器gossip的信息
            if msg[0].type == 'pro_block':
                print('recvd a problock from client, now publish it')
                time.sleep(0.05)
                self.communicator.SendMsgBuffer.push(msg[0], msg[1])
            elif msg[0].type == 'reduction':
                self.communicator.SendMsgBuffer.push(msg[0], msg[1])
            elif msg[0].type == 'consensus':
                self.communicator.SendMsgBuffer.push(msg[0], msg[1])
            # 后三个是服务器需要处理和存储的信息
            elif msg[0].type == 'final_consensus':
                self.communicator.AppendBlockSigBuffer.push(msg[0], msg[1])
            elif msg[0].type == 'tentative_consensus':
                self.communicator.AppendBlockSigBuffer.push(msg[0], msg[1])
            elif msg[0].type == 'txblock_sig':
                self.communicator.TxBlockSigBuffer.push(msg[0], msg[1])
            elif msg[0].type == 'proof_sig':
                self.communicator.TeeProofSigBuffer.push(msg[0], msg[1])
            else:
                print('wrong msg')

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
        shard_length = len(self.node_storage.proposal_block[1])+1
        previous_hash = self.node_storage.proposal_block[1][-1].decode()
        block = ProBlock(
            1, shard_length, previous_hash, None, None, None)
        print('block num and previous hash:', shard_length, previous_hash)
        return block

    def AppendBlock(self):
        counts = 0
        pro_block = ProBlock(1, len(
            self.node_storage.proposal_block[1])+1, '0', None, None, None)
        pro_block_msg = message(public_key=self.public_key, sig=signing(
            pickle.dumps(pro_block), self.private_key), msgtype='Problock', sign_msg=pro_block)
        self.communicator.ProBlockMsgBuffer.push(
            pro_block_msg, random.randint(1, 2000))
        while True:
            # 暂不记录投票人的信息，只要投票数够了就上链
            while self.communicator.AppendBlockSigBuffer.getLength() <= 0:
                continue
            msg = self.communicator.AppendBlockSigBuffer.pop()
            votes = msg[0].sign_msg['votes']
            counts = counts + votes
            print(counts)
            if counts > 2/3*config.NODE_NUM:
                self.node_storage.proposal_block[self.shard_id].append(
                    msg[0].sign_msg['consensus_block'])
                print(self.node_storage.proposal_block[self.shard_id])
                counts = 0
                time.sleep(5)
                print('Append a problock')
                logging.info('************Append a problock!************')
                # 发送problock
                pro_block = self.generate_problock()
                pro_block_msg = message(public_key=self.public_key, sig=signing(
                    pickle.dumps(pro_block), self.private_key), msgtype='Problock', sign_msg=pro_block)
                self.communicator.init_buffer()
                self.communicator.ProBlockMsgBuffer.push(
                    pro_block_msg, random.randint(1, 2000))
                # 清空所有buffer（除了同步buffer），确保不再发送消息（但是要处理移动节点超时上传的msg

    def generate_txblock(self):
        # 花0.5秒来创建txblock, 省略打包步骤
        # while self.TxblockflagBuffer.getLength() <= 0:
        while len(self.node_storage.proposal_block[1]) <= 0:
            continue
        tx_block = TxBlock(
            1, len(self.node_storage.proposal_block[1]), None)
        # print(len(self.node_storage.proposal_block[1]))
        tx_block_msg = message(public_key=self.public_key, sig=signing(
            pickle.dumps(tx_block), self.private_key), msgtype='Txblock', sign_msg=tx_block)
        # print('生成txblock的位置:', len(self.node_storage.proposal_block[1]))
        self.communicator.TxBlockMsgBuffer.push(
            tx_block_msg, random.randint(2, 10000))

    def CollectTxblock(self):
        while self.communicator.TxBlockSigBuffer.getLength() <= 0:
            continue
        txblock, priority = self.communicator.TxBlockSigBuffer.pop()
        if priority != 0:
            # 根据timestamp进行排序
            self.node_storage.transaction_block_pool[len(
                self.node_storage.proposal_block[self.shard_id])].append(txblock.sign_msg)
            self.node_storage.transaction_block_pool[len(self.node_storage.proposal_block[self.shard_id])] = sorted(
                self.node_storage.transaction_block_pool[len(self.node_storage.proposal_block[self.shard_id])], key=lambda x: x.timestamp)
            # print('收到了带有签名的txblock')

    def tx_validation(self):
        # 单个txblock的验证时间为
        problock_num = len(self.node_storage.proposal_block[self.shard_id]) - 3
        count = 1
        # print('************当前块为: ', problock_num)
        # print(self.node_storage.transaction_block_pool[problock_num])
        if problock_num > 0:
            for txblock in self.node_storage.transaction_block_pool[problock_num]:
                if len(self.node_storage.proposal_block[self.shard_id]) - 3 != problock_num:
                    break
                print('当前交易验证的块是: ', problock_num)
                print('当前共识块的长度为: ',
                      len(self.node_storage.proposal_block[self.shard_id]) - 3)
                # msg中可以模拟验证的成功率，比如生成一个1-100随机数，1-5则验证失败
                num = random.randint(1, 100)
                # if num > 5:
                #     merkleroot = 'NewMerkleRoot'
                # else:
                #     merkleroot = 'OldMerkleRoot'
                merkleroot = 'NewMerkleRoot'
                sign_msg = {'num': num, 'merkleroot': merkleroot,
                            'problock_num': problock_num, 'txblock_num': count}
                proof = message(public_key=self.public_key, sig=signing(
                    pickle.dumps(sign_msg), self.private_key), msgtype='Teeproof', sign_msg=sign_msg)
                proof.togossip = False
                self.communicator.SysnMsgBuffer.push(
                    proof, random.randint(2, 10000))
                self.communicator.TeeProofMsgBuffer.push(
                    proof, random.randint(2, 10000))
                num1 = len(
                    self.node_storage.transaction_block_pool[problock_num]) - count
                print('tee待验证交易块数量:', num1)
                if num1 == 0:
                    self.node_storage.transaction_block_pool[problock_num] = []
                    break
                count = count + 1
        while len(self.node_storage.proposal_block[self.shard_id]) - 3 == problock_num:
            # print(12312412413242312312312312132)
            continue

    def AppendTxblock(self):
        # 需要由不同tee签名的txblock才可以上链
        count = {}
        pro_num = len(self.node_storage.proposal_block[1]) - 3
        # 超时机制
        to = True
        if pro_num > 0:
            print('进入循环前的pro_num', pro_num)
            while to:
                if len(self.node_storage.proposal_block[1])-3 != pro_num:
                    break
                start = time.time()
                while self.communicator.TeeProofSigBuffer.getLength() <= 0:
                    if time.time() > start + config.EXPIRED_THRESHOLD:
                        to = False
                        break
                    continue
                if to:
                    msg, priority = self.communicator.TeeProofSigBuffer.pop()
                    if priority != 0:
                        # print(count)
                        print('收到的probloc_num, 应该收到的层数：', msg.sign_msg['problock_num'], len(
                            self.node_storage.proposal_block[1]) - 3)
                        if msg.sign_msg['problock_num'] > len(self.node_storage.proposal_block[1]) - 3:
                            break
                        if msg.sign_msg['problock_num'] < len(self.node_storage.proposal_block[1]) - 3:
                            continue
                        print('append a txblock!')
                        if not str(msg.sign_msg['txblock_num']) in count.keys():
                            count[str(msg.sign_msg['txblock_num'])] = 1
                        else:
                            count[str(msg.sign_msg['txblock_num'])] = count[str(
                                msg.sign_msg['txblock_num'])] + 1
            print('problock_num, 其中各个txblock收到的teeproofsig数量:', pro_num, count)
            for key in count:
                if count[key] > 2/3 * config.TEE_NUM:
                    self.node_storage.transaction_block[pro_num].append(key)
            print('problock_num, txblocks:', pro_num,
                  self.node_storage.transaction_block[pro_num])
            while len(self.node_storage.proposal_block[1])-3 == pro_num:
                continue
            # print(self.node_storage.transaction_block[len()])
