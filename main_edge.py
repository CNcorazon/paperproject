
import threading
import time

from edge_node import EdgeNode
from cryptography.hazmat.primitives import serialization

'''
边缘节点接受每一轮中的投票
'''


class RecvVoteMsgsThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(RecvVoteMsgsThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.recvmsgs()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class SendGossipVoteThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(SendGossipVoteThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while True:
            # voters = []
            # # counts 按照value降序排列
            # counts = {}
            # start = time.time()
            # while True:
            #     if not self.node.VoteMsgBuffer.empty():
            #         break
            # while True:
            # m = q.get_nowait()
            # if self.node.VoteMsgBuffer.empty():
            #     if time.time() > start + 10:
            #        # 单个边缘节点完成投票之后，开始gossip投票结果
            #         print('Time out!')
            #         self.node.gossipvoterst(counts)
            #         break
            # else:
            #     start = time.time()
            m = self.node.VoteMsgBuffer.get()
            self.node.sendgossipvote(m)
            # self.node.GossipMsgBuffer.put(m)
            # votes, value = self.node.ProcessMsg(ctx, num, m)
            # votes = 1
            # value = 0
            # if (m[0] in voters) or votes == 0:
            #     continue
            # voters.append(m[0])
            # if not value in counts.keys():
            #     counts[value.decode()] = votes
            # else:
            #     counts[value.decode()] = counts[value.decode()] + votes
            # counts = sorted(counts.items(), key=lambda kv: (
            #     kv[1], kv[0]), reverse=True)
            # # 单个节点统计投票数完成后，开始gossip投票结果
            # if counts[0][1] > 3:
            #     print('begin gossip value: ', value)
            #     break

            # '''
            # 如果vote超过2/3，返回hblock1，否则返回empty_hash，这个应该是移动节点做
            # '''
            # while not self.node.GossipMsgBuffer.empty():
            #     vote_dict = self.node.GossipMsgBuffer.get()
            #     for key, value in vote_dict:
            #         # 也要检查该移动节点是否向不同的服务器发送了消息
            #         if key not in counts.keys():
            #             counts[key] = value
            #         else:
            #             counts[key] = counts[key] + value
            #     counts = sorted(counts.items(), key=lambda kv: (
            #         kv[1], kv[0]), reverse=True)

            # # 定义一下empty_block
            # if counts[0][1] > 2/3 * num:
            #     voterst = {b'1': b'hblock1'}  # {id:hashofblock} id sorthash
            # else:
            #     voterst = {b'0': b'hempty'}
            # print('gossip finished! Outcome is: ', voterst)


class RecvGossipVoteThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(RecvGossipVoteThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.recvgossipvote()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class SendVoteMsgThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(SendVoteMsgThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        start = time.time()
        flag = 1
        while self.__running.isSet():
            while not self.node.GossipMsgBuffer.empty():
                start = time.time()
                vote = self.node.GossipMsgBuffer.get()
                self.node.sendmsgs(vote)
                flag = 0
            if self.node.GossipMsgBuffer.empty() and flag == 0:
                if time.time() > start + 10:
                    print("Thread4: --------GOSSIP END--------")
                    self.node.sendmsgs([b'0', b'0', b'0'])
                    flag = 1

    def stop(self):
        self.__flag.set()
        self.__running.clear()


def main():
    node = EdgeNode(1)
    RecvVote_thread = RecvVoteMsgsThread(node)
    SendGossip_thread = SendGossipVoteThread(node)
    RecvGossip_thread = RecvGossipVoteThread(node)
    SendVote_thread = SendVoteMsgThread(node)
    RecvVote_thread.start()
    SendGossip_thread.start()
    RecvGossip_thread.start()
    SendVote_thread.start()

    # print(threading.active_count())
    # print(threading.enumerate())
    # print(threading.current_thread())


if __name__ == '__main__':
    main()
