from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa


private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend())
public_key = private_key.public_key()

msg = [public_key, '123']
msg1 = [21, msg]
print(msg1)
