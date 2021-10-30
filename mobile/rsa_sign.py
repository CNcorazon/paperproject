from cryptography.hazmat import backends
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import os


def generate_private_key():
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    return private_key


def generate_public_key(private_key):
    public_key = private_key.public_key()
    return public_key


def read_private_key():
    with open("private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
        )
    return private_key


def read_public_key():
    with open("public_key.pem", "rb") as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
        )
    return public_key


def signing(msg, private_key):
    signature = private_key.sign(
        msg,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def verification(public_key, sig, msg):
    try:
        public_key.verify(
            sig,
            msg,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("ValidSignature")
        return True
    except Exception as e:
        print("InvalidSignature", e)
        return False


def save_public_key(public_key, pem_name):
    # 将公钥编码为PEM格式的数据
    pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    # 将PEM个数的数据写入文本文件中
    with open(pem_name, 'w+') as f:
        f.writelines(pem.decode())


def save_private_key(private_key, pem_name):
    # 将私钥编码为PEM格式的数据
    pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    # 将PEM个数的数据写入文本文件中
    with open(pem_name, 'w+') as f:
        f.writelines(pem.decode())


if __name__ == '__main__':
    msg = b"A message I want to sign"
    if os.path.exists('private_key.pem'):
        private_key = read_private_key()
    else:
        private_key = generate_private_key()
        save_private_key(private_key, 'private_key.pem')

    sig = signing(msg, private_key)
    public_key = generate_public_key(private_key)
    save_public_key(public_key, 'public_key.pem')
    print(verification(public_key, sig, msg))

    p = read_public_key()

    print(verification(p, sig, msg))
