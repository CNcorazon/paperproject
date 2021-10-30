import pickle
import queue
import zmq
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from rsa_sign import *

# 先统一压缩成bytes文件，并附上相应的type，如'tx_block''consensus_vote'等


class message():
    def __init__(self, public_key, sig, msgtype, sign_msg):
        self.sign_msg = sign_msg
        self.type = msgtype
        self.pk_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        self.sig = sig
        self.togossip = True

    def update_weight(self, weight, totalweight):
        self.sign_msg['weight'] = weight
        self.sign_msg['totalweight'] = totalweight


if __name__ == '__main__':
    sign_m = {'round': 5, 'step': 2, 'pi': b'123',
              'hprev': b'123', 'value': '13123', 'weight': 0, 'totalweight': 0}
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    public_key = private_key.public_key()
    sig = signing(pickle.dumps(sign_m), private_key)
    message1 = message(public_key, sig, 'consensus_vote', sign_m)
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5555")
    socket.send_pyobj(message1)
    msg1 = socket.recv()
    print(msg1)
