'''
实现了algorand中的委员会选举方法，hash越大该移动节点占得投票份额越大
'''

import hashlib
import time
import rsa_vrf
import binascii
import math
from numpy import random
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from rsa_sign import *
# Sortition(sk,seed,num of committee members,weight,total weight) --> vrf_proof,num of votes
# seed --> <N,block*n-1>


def Sortiiton(sk, seed, num, w, W):
    pi = rsa_vrf.get_vrf(seed, sk)
    pi_bin = bin(int(binascii.hexlify(pi), 16))
    hashlen = len(pi_bin)
    p = num/W
    prob = (int(pi_bin, 2)*4)/(2**hashlen)
    j = 0
    left = 0
    right = 0
    while True:
        tmp = math.factorial(
            w) // ((math.factorial(j) * math.factorial(w-j)))
        tmp = tmp * (p**j) * ((1-p)**(w-j))
        left = right
        right = right + tmp
        if prob >= left and prob < right:
            break
        j = j+1
    return pi, j


def VerifySort(pk, pi, seed, num, w, W):
    if not rsa_vrf.VRF_verifying(pk, seed, pi, 20):
        return 0
    pi_bin = bin(int(binascii.hexlify(pi), 16))
    hashlen = len(pi_bin)
    p = num/W
    prob = (int(pi_bin, 2)*4)/(2**hashlen)
    j = 0
    left = 0
    right = 0
    while True:
        tmp = math.factorial(
            w) // ((math.factorial(j) * math.factorial(w-j)))
        tmp = tmp * (p**j) * ((1-p)**(w-j))
        left = right
        right = right + tmp
        if prob >= left and prob < right:
            break
        j = j+1
    return j


if __name__ == '__main__':
    shard_data = str(5) + str(40)
    time_data = str(random.randint(10, 112312455121))
    data = shard_data + time_data + str(1233)
    seed = str(10) + hashlib.sha256(data.encode('utf-8')).hexdigest()
    num = 10
    w = 10
    W = 10*100
    private_key = read_private_key()
    public_key = read_public_key()
    pi, j = Sortiiton(private_key, seed, num, w, W)
    j1 = VerifySort(public_key, pi, seed, num, w, W)
    print('票数为:', j1)
