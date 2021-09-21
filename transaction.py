import hashlib
import random
import rsa_sign


class Tx():
    '''
    交易内容有id、sender、recipient、amount、intershard
    除了sender的签名之外，还需要包括移动节点的见证签名
    '''

    def __init__(self,
                 sender,
                 recipient,
                 amount,
                 timestamp,
                 sk):
        self.id = random.randrange(10**30, 10**31)
        self.sender = sender
        self.recipient = recipient
        self.amount = amount
        self.timestamp = timestamp
        self.intershard = self._is_intershard()
        # witness_sig = [pk, sig]
        self.witness_sig = []
        if sk == None:
            self.sig = None
        else:
            self.sig = rsa_sign.signing(self.get_str(), sk).hex()
            self.public_key = rsa_sign.generate_public_key(sk)

    def get_str(self):
        result = '%s %s %d %f' % (
            self.sender, self.recipient, self.amount, self.timestamp)
        return result.encode()

    def witness(self, pk, sig):
        self.witness_sig.append([pk, sig])

    def verify_tx(self):
        return rsa_sign.verification(self.public_key, self.sig, self.get_str())
