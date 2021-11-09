import hashlib

value = hashlib.sha256('123'.encode()).hexdigest().encode()
print(value)
