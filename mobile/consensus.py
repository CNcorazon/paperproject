import time
import logging
import config
from message import message
from rsa_sign import *
import pickle
import CommonCoin


class consensus(self):
    def __init__(self):

    def BAstar(self):
        logging.info('************Consensus begin*********')
        print('consensus begin')
        print('Reduciton begin')
        hblock = self.Reduction()
        print('Reduction end')
        print('BinaryBA begin')
        time.sleep(3)
        hblock_star = self.BinaryBA(hblock)
        print('BinaryBA end')
        # print(1)
        # 检查是fianl/tentative共识,1:final,0:tentative
        print('count vote begin')
        r = self.CountVote(config.FINAL)
        print('count vote end')
        # print(2)
        # 清空接受消息列表
        self.communicator.consensus_flag = False
        self.communicator.init_buffer()
        if hblock_star == r:
            print('send result begin')
            msg = message(public_key=self.public_key, sig=signing(pickle.dumps({'consensus_block': hblock_star, 'votes': self.node_storage.votes}), self.private_key),
                          msgtype='final_consensus', sign_msg={'consensus_block': hblock_star, 'votes': self.node_storage.votes})
            self.communicator.SendMsgBuffer.push(msg, 1)
            self.node_storage.previous_hash = hblock_star.decode()
            logging.info('************Consensus end*********')
            logging.info('FINAL consensus is:')
            try:
                logging.info(hblock_star.decode())
            except:
                logging.info(hblock_star)
            print('send result end')
            print('consensus end')
        else:
            print('send tentative consensus result')
            msg = message(public_key=self.public_key, sig=signing(pickle.dumps({'consensus_block': hblock_star, 'votes': self.node_storage.votes}), self.private_key),
                          msgtype='tentative_consensus', sign_msg={'consensus_block': hblock_star, 'votes': self.node_storage.votes})
            self.communicator.SendMsgBuffer.push(msg, 1)
            self.node_storage.previous_hash = hblock_star.decode()
            logging.info('************Consensus end*********')
            logging.info('TENTATIVE consensus is:')
            try:
                logging.info(hblock_star.decode())
            except:
                logging.info(hblock_star)
            print('send result end')
            print('consensus end')

    def BinaryBA(self, block_hash):
        # '00' means TIMEOUT '0'means emptyhash
        step = 1
        r = block_hash
        print('hblock is:', r)
        while step < config.MAXSTEP:
            # print(0)
            self.CommitteeVote(step, r)
            # print(1)
            r = self.CountVote(step)
            # print(2)
            if r == 'timeout':
                r = block_hash
            elif r != 'empty_block':
                self.CommitteeVote(step+1, r)
                self.CommitteeVote(step+2, r)
                self.CommitteeVote(step+3, r)
                if step == 1:
                    self.CommitteeVote(config.FINAL, r)
                # print('end')
                return r
            step = step + 1

            self.CommitteeVote(step, r)
            r = self.CountVote(step)
            if r == 'timeout':
                r = 'empty_block'
            elif r == 'empty_block':
                self.CommitteeVote(step+1, r)
                self.CommitteeVote(step+2, r)
                self.CommitteeVote(step+3, r)
                return r
            step = step + 1

            self.CommitteeVote(step, r)
            r = self.CountVote(step)
            if r == 'timeout':
                if CommonCoin() == 0:
                    r = block_hash
                else:
                    r = 'empty_block'
            step = step + 1

    def Reduction(self):
        logging.info('************begin reduction************')
        # 该步骤的目的是将consensus on arbitrary value转化为consensus on binary value, i.e. {block_hash, empty_hash}
        # 从candidate中选出vrf最小的作为自己本地的胜者，检查proposal block中的交易是否有超过2/3的签名，检查global root的签名是否超过2/3
        while self.communicator.RecvMsgBuffer.getLength() <= 0:
            print(12312)
            continue
        msg, priority = self.communicator.RecvMsgBuffer.pop()
        while msg.type != 'pro_block':
            print(msg.sign_msg)
            print(123123)
            msg, priority = self.communicator.RecvMsgBuffer.pop()
        # print('msg is:', msg.sign_msg)
        # print('priority is:', priority)
        pro_block = msg.sign_msg
        print('本轮共识的区块层数:', pro_block.shard_length)
        print('本轮共识的区块的hprev:', pro_block.previous_hash)
        self.node_storage.N = pro_block.shard_length
        self.node_storage.previous_hash = pro_block.previous_hash
        start = time.time()
        winner = pro_block
        tmp = int(binascii.hexlify(pro_block.vrf).decode()[-5:], 16)
        # 超时机制
        to = True
        while to:
            while self.communicator.RecvMsgBuffer.getLength() <= 0:
                if time.time() > start + config.EXPIRED_THRESHOLD:
                    to = False
                    break
                continue
            if to:
                msg, priority = self.communicator.RecvMsgBuffer.pop()
                if msg.type == 'pro_block':
                    pro_block = msg.sign_msg
                    print('收到了一个problock', pro_block, int(
                        binascii.hexlify(pro_block.vrf).decode()[-5:], 16))
                    if int(binascii.hexlify(pro_block.vrf).decode()[-5:], 16) < tmp:
                        winner = pro_block
                        tmp = int(binascii.hexlify(
                            pro_block.vrf).decode()[-5:], 16)
        print(winner.get_str())
        # 首先验证block的签名
        verification(winner.get_publickey(), winner.sig, winner.get_str())
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
        value = hashlib.sha256(winner.get_str()).hexdigest().encode()
        sig = signing(value, self.private_key)
        msg = message(self.public_key, sig, 'reduction', value)
        self.communicator.SendMsgBuffer.push(msg, random.randint(2001, 5000))
        hblock = self.CountVote(0)
        logging.info('************reduction end************')
        logging.info('hblock is:')
        try:
            logging.info(hblock.decode())
        except:
            logging.info(hblock)
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
        _round = self.node_storage.N
        sign_m = {'round': _round, 'step': _step, 'pi': pi,
                  'hprev': hprev, 'value': value, 'weight': weight, 'totalweight': totalweight}
        sig = signing(pickle.dumps(sign_m), sk)
        msg = message(public_key=pk, sig=sig,
                      msgtype='consensus', sign_msg=sign_m)
        # 随机生成priority
        self.communicator.SendMsgBuffer.push(msg, random.randint(5001, 10000))

    def CountVote(self, step):
        counts = {}
        voters = []
        # 这边用了两个timeout，原因是没有找到合适的方法去按照round和step表示incomingMsgs[round,step]
        if step == 0:
            # print('reduction中的countvote')
            to = True
            while to:
                start = time.time()
                while self.communicator.RecvMsgBuffer.getLength() <= 0:
                    if time.time() > start + config.EXPIRED_THRESHOLD:
                        to = False
                        break
                    continue
                if to:
                    m, priority = self.communicator.RecvMsgBuffer.pop()
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
                    # print('收到的投票数量:', count_[0][1])
                    if count_[0][1] > 2/3 * self.node_storage.node_num:
                        return count_[0][0]
            return 'timeout'
        else:
            # print('binaryBA中的countvote')
            to = True
            start = time.time()
            while to:
                # print(1)
                start1 = time.time()
                while self.communicator.RecvMsgBuffer.getLength() <= 0:
                    if time.time() > start1 + config.EXPIRED_THRESHOLD:
                        # print(2)
                        to = False
                        break
                    continue
                if to:
                    # print(3)
                    m = self.communicator.RecvMsgBuffer.pop()
                    # print(4)
                    #  这一步是保证取出的msg是正确的round和step，若不是，则重新赋一个随机prority,push进去。
                    if m[0].type == 'reduction' or m[0].sign_msg['round'] != self.node_storage.N or m[0].sign_msg['step'] != step:
                        self.communicator.RecvMsgBuffer.push(m[0], 10001)
                        # print(5)
                        if time.time() > start + config.EXPIRED_THRESHOLD:
                            # print(6)
                            return 'timeout'
                        continue
                    # print(7)
                    votes, value = self.ProcessMsg(m[0])
                    # 投票先都为一票，与权重无关，不采用PoS
                    # print(5)
                    if (m[0].pk_pem in voters) or votes == 0:
                        continue
                    # print(6)
                    voters.append(m[0].pk_pem)
                    # print(value)
                    if not value in counts:
                        # print(7)
                        counts[value] = votes
                        # print(counts)
                    else:
                        # print(8)
                        counts[value] = counts[value] + votes
                    count_ = sorted(counts.items(), key=lambda kv: (
                        kv[1], kv[0]), reverse=True)
                    start = time.time()
                    # 当收到的投票大于阈值之后，返回hblock
                    # print('收到投票数量:', count_[0][1])
                    if count_[0][1] > 2/3 * self.node_storage.node_num:
                        return count_[0][0]
            return 'timeout'
