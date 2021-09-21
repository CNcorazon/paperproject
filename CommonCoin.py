'''
当某一轮中移动节点收到的关于{block_hash, empty_hash}的投票都没有达到阈值时，使用该函数随机确定一个值
简化版
'''
import random


def CommonCoin():
    num = random.randint(0, 1)
    return num
