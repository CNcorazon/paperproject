from cryptography.hazmat.primitives import serialization
import zmq
from rsa_sign import read_public_key

context = zmq.Context()
print("Connecting to server...")
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:5555")

# 将公钥发送过去，先读取本地的pk，将RSA对象转换成字节码pem之后，再传输string
pk = read_public_key()
pem = pk.public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo
)
msg = pem.decode()
socket.send_string(msg)

msg = socket.recv()
print(msg)
