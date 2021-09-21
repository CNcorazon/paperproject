from sortition import Sortiiton
from cryptography.hazmat.primitives import serialization
import zmq
import hashlib
from rsa_sign import *

context = zmq.Context()
print("Connecting to server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")


_round = 5
num = 10
w = 40
W = 100
value = 1
last_block = b'1234'
seed = str(_round) + hashlib.sha256(last_block).hexdigest()
sk = read_private_key()
pi, j = Sortiiton(sk, seed, num, w, W)


# 将公钥发送过去，先读取本地的pk，将RSA对象转换成字节码pem之后，再传输string
pk = read_public_key()
pem = pk.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
msg = str(_round) + str(' ') + str(pi) + str(' ') + \
    str(last_block) + str(' ') + str(value)
msg = msg.encode()
sig = (signing(msg, sk))


socket.send_multipart([pem, sig, msg])

msg = socket.recv()
print(msg)
