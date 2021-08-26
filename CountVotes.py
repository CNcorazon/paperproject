import time
from sortition import *
from rsa_sign import verification


# 通过0mq获得缓冲消息队列incomingMsgs
# msg = incomingMsgs.next()
# 如果在一定时间内没有收到足够的msg，timeout
# ProcessMsg(ctx,expected number of users,msg)-->value,#votes(vrf sortition过程中每个人vrf值不同则vote个数也不同)

# T投票的阈值，一般为2/3，num为预期从sortition中选出委员会成员的数量
def CountVotes(ctx, round, step, T, num, windowT):
    voters = []
    counts = []
    start = time.time()
    while True:
        m = msgs.next()
        if m == None:
            if time.time() > start+windowT:
                return 'Timeout! Begin gossip'
        else:
            votes, value = ProcessMsg(ctx, num, m)
            if (m[0] in voters) or votes == 0:
                continue
            voters.append(m[0])
            counts[value] = counts[value] + votes
            # 单个节点统计投票数完成后，开始gossip投票结果
            if counts[value] > T*num:
                return value


# 验证签名，并且验证其委员会成员身份
def ProcessMsg(ctx, num, msg):
    # ⟨pk,signed_m⟩ ← msg
    # ⟨round,step,π,hprev,value⟩ ← signed_m
    pk = msg[0]
    signed_m = msg[1]
    if not verification(pk, sig, signed_m):
        return 0, None, None
    _round = signed_m[0]
    _step = signed_m[1]
    pi = signed_m[2]
    hprev = signed_m[3]
    value = signed_m[4]
    if hprev != ctx.last_block:
        return 0, None, None
    # 每个节点各自存有ctx 中存有上个块的hash，层数，可以算出seed；各自的权重w，总权重W
    votes = VerifySort(pk, pi, ctx.seed, num, ctx.weight[pk], ctx.W)
    return votes, value
