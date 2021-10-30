

from message import *
import zmq
from util import PriorityQueue
from zmq.sugar import socket
from queue import Queue

buffer1 = PriorityQueue()
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")
msg = socket.recv_pyobj()
buffer1.push(msg, 12)
socket.send_string('Send successfully!')
msg2, priority = buffer1.pop()
msg2.update_weight(5, 5)
print(msg2)
print(msg2.sign_msg, msg2.type)
