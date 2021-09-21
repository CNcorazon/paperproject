from rsa_sign import *
from cryptography.hazmat.primitives import hashes
import threading


# def recv_voterst(node):
#     voterst = node.communicator.rec_voterst()
#     proposer = voterst[0][0]
#     hashofblock = voterst[0][1]
#     return proposer, hashofblock


# def revote(proposer, hblock, node, _step):
#     pk = proposer
#     value = hblock
#     hprev = node.hprev
#     pi = node.pi
#     _round = node.N
#     sign_m = [_round, _step, pi, hprev, value]
#     msg = [pk, sign_m]
#     node.communicator.send_vote(msg)


# 加一个CountVotebuffer，用于接受消息


def main():
    # 计算各自的vrf

    # 某个服务器向a发送了虚假的投票信息，以至于a收到了超过一定阈值的投票，a对于hblock已经达到了共识。
    # BinaryBA需要保证下一轮中大家都对这个hblock投票
