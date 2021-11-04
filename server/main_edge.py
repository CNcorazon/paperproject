
import threading
import time
import logging
from edge_node import EdgeNode
from cryptography.hazmat.primitives import serialization

'''
边缘节点接受每一轮中的投票
'''
logging.basicConfig(
    format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S', level=logging.INFO, filemode='w', filename='server.log')


class RecvMsgsThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(RecvMsgsThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.recvmsgs()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class SendGossipVoteThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(SendGossipVoteThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.sendgossipmsg()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class SendMsgThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(SendMsgThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.sendmsgs()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class MessageForwardThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(MessageForwardThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.message_forwarding()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class SendProblockThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(SendProblockThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.sendproblock()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class SendTxblockThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(SendTxblockThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.sendtxblock()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class SendTeeProofThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(SendTeeProofThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.sendteeproof()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class AppendBlockThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(AppendBlockThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.AppendBlock()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class GenerateTxblockThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(GenerateTxblockThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.generate_txblock()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class TxValidationThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(TxValidationThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.tx_validation()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class CollectTxblockThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(CollectTxblockThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.CollectTxblock()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class AppendTxblockThread(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(AppendTxblockThread, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.AppendTxblock()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


def main():
    node = EdgeNode(1)
    RecvMsg_thread = RecvMsgsThread(node)
    SendGossip_thread = SendGossipVoteThread(node)
    SendMsg_thread = SendMsgThread(node)
    MessageForward_thread = MessageForwardThread(node)
    SendProblock_thread = SendProblockThread(node)
    SendTxblock_thread = SendTxblockThread(node)
    SendTeeProof_thread = SendTeeProofThread(node)
    AppendBlock_thread = AppendBlockThread(node)
    GenerateTxblock_thread = GenerateTxblockThread(node)
    TxValidation_thread = TxValidationThread(node)
    CollectTxblock_thread = CollectTxblockThread(node)
    AppendTxblock_thread = AppendTxblockThread(node)
    RecvMsg_thread.start()
    # SendGossip_thread.start()
    SendMsg_thread.start()
    MessageForward_thread.start()

    SendProblock_thread.start()
    AppendBlock_thread.start()

    GenerateTxblock_thread.start()
    SendTxblock_thread.start()
    CollectTxblock_thread.start()

    TxValidation_thread.start()
    SendTeeProof_thread.start()
    AppendTxblock_thread.start()


if __name__ == '__main__':
    main()
