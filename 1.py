# import hashlib

# from mobile.message import message
# from cryptography.hazmat.primitives import serialization
# from cryptography.hazmat.primitives.asymmetric import padding
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.primitives.asymmetric import rsa
# from cryptography.hazmat.backends import default_backend
# from mobile import block
# import time
# import json
# import pickle

list1 = []
for _ in range(10):
    list1.append([])
list1[1].append(123)
print(list1[1][-1])
# father_list = []
# for i in range(10):
#     storage = []
#     father_list.append(storage)
# _step1 = 1
# _step2 = 2

# print(father_list)
# father_list[_step1].append([[123, 12], 1, _step1, 123, b'123'])
# print(father_list)


# t = (1, 31, 13)
# t = list(t)
# t.append(23)

# # t = t.append(1231)
# print(t)

# print(b'1' == b'1')

# a = str(10) + hashlib.sha256(str(123).encode('utf-8')).hexdigest()
# print(type(hashlib.sha256(str(123).encode('utf-8')).hexdigest()))
# # print(a)

# # print('123'.encode('utf-8').decode('utf-8'))

# list1 = [[], []]
# print(len(list1[0]))

# print(2/3 * 4)


# valuedic = {'123': 21, '12314': 512}
# valuedic_ = sorted(valuedic.items(), key=lambda kv: (
#     kv[1], kv[0]), reverse=True)
# print(valuedic_[0][1])

# problock = []
# for _ in range(5):
#     problock.append([])
# print(problock)

# while True:
#     print(1)
#     while True:
#         print(2)
#         break
#         print(3)

# from message import message
# from util import *
# import threading
# import time
# from queue import Queue


# def job(l, q):
#     # q.push('123', 1)
#     msg = message('consensus', '123')
#     q.push(msg, 12312)
#     print('end')


# def job2(q):
#     item = q.pop()
#     print(item[0].type)


class sad():
    def __init__(self, ahah):
        self.ahah = ahah


def main():
    happy = sad(123)
    list1 = []
    dict1 = {'1': 11, '2': 22, '3': 33}

    # private_key = rsa.generate_private_key(
    #     public_exponent=65537,
    #     key_size=2048,
    #     backend=default_backend())
    # public_key = private_key.public_key()
    # msg = {'sig': b'213', 'sign_m': b'12312'}
    # msg1 = pickle.dumps(msg)
    # msg2 = pickle.dumps(msg)
    # print(msg1, type(msg1))
    # print(msg2, type(msg2))
    # buffer = PriorityQueue()
    # l = 1
    # thread1 = threading.Thread(target=job, args=(l, buffer))
    # thread2 = threading.Thread(target=job2, args=(buffer,))
    # thread1.start()
    # thread2.start()
    # item = buffer.pop()
    # print(item)
    # buffer.push(item[0], item[1])
    # print(buffer.pop())


if __name__ == '__main__':
    main()
