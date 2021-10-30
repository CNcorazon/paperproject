#  1 //                                                          _ooOoo_
#  2 //                                                         o8888888o
#  3 //                                                         88" . "88
#  4 //                                                         (| -_- |)
#  5 //                                                          O\ = /O
#  6 //                                                      ____/`---'\____
#  7 //                                                    .   ' \\| |// `.
#  8 //                                                     / \\||| : |||// \
#  9 //                                                   / _||||| -:- |||||- \
# 10 //                                                     | | \\\ - /// | |
# 11 //                                                   | \_| ''\---/'' | |
# 12 //                                                    \ .-\__ `-` ___/-. /
# 13 //                                                 ___`. .' /--.--\ `. . __
# 14 //                                              ."" '< `.___\_<|>_/___.' >'"".
# 15 //                                             | | : `- \`.;`\ _ /`;.`/ - ` : | |
# 16 //                                               \ \ `-. \_ __\ /__ _/ .-` / /
# 17 //                                       ======`-.____`-.___\_____/___.-`____.-'======
# 18 //                                                          `=---='
# 19 //
# 20 //                                       .............................................
# 21 //                                              佛祖保佑             永无BUG
# 22 //                                      佛曰:
# 23 //                                              写字楼里写字间，写字间里程序员；
# 24 //                                              程序人员写程序，又拿程序换酒钱。
# 25 //                                              酒醒只在网上坐，酒醉还来网下眠；
# 26 //                                              酒醉酒醒日复日，网上网下年复年。
# 27 //                                              但愿老死电脑间，不愿鞠躬老板前；
# 28 //                                              奔驰宝马贵者趣，公交自行程序员。
# 29 //                                              别人笑我忒疯癫，我笑自己命太贱；
# 30 //                                              不见满街漂亮妹，哪个归得程序员？


from rsa_sign import *
from cryptography.hazmat.primitives import hashes
import threading
from mobile_node import *


class Thread1(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(Thread1, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            flag, hblock_star = self.node.BAstar()
            print('------Consensus is over------:', flag, hblock_star)

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class Thread2(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(Thread2, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.signing_txblock()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class Thread3(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(Thread3, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.signing_teeproof()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class Thread4(threading.Thread):
    def __init__(self, node, *args, **kwargs):
        super(Thread4, self).__init__(*args, **kwargs)
        self.node = node
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.propose_block()

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class Thread5(threading.Thread):
    def __init__(self, node, serverip, *args, **kwargs):
        super(Thread5, self).__init__(*args, **kwargs)
        self.node = node
        self.serverip = serverip
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.send_msg(self.serverip)

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class Thread6(threading.Thread):
    def __init__(self, node, serverip, *args, **kwargs):
        super(Thread6, self).__init__(*args, **kwargs)
        self.node = node
        self.serverip = serverip
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.recv_msg(self.serverip)

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class Thread7(threading.Thread):
    def __init__(self, node, serverip, *args, **kwargs):
        super(Thread7, self).__init__(*args, **kwargs)
        self.node = node
        self.serverip = serverip
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.recv_problockmsg(self.serverip)

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class Thread8(threading.Thread):
    def __init__(self, node, serverip, *args, **kwargs):
        super(Thread8, self).__init__(*args, **kwargs)
        self.node = node
        self.serverip = serverip
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.recv_txblockmsg(self.serverip)

    def stop(self):
        self.__flag.set()
        self.__running.clear()


class Thread9(threading.Thread):
    def __init__(self, node, serverip, *args, **kwargs):
        super(Thread9, self).__init__(*args, **kwargs)
        self.node = node
        self.serverip = serverip
        self.__flag = threading.Event()
        self.__flag.set()
        self.__running = threading.Event()
        self.__running.set()

    def run(self):
        while self.__running.isSet():
            self.node.recv_teeproof(self.serverip)

    def stop(self):
        self.__flag.set()
        self.__running.clear()


def main():
    serverip = '172.19.5.8'
    # serverip1 = '10.211.55.4'

    node = MobileNode('172.19.5.8', 1, 2, 1)
    node.node_storage.set_N(5)

    thread1 = Thread1(node)
    thread2 = Thread2(node)
    thread3 = Thread3(node)
    thread4 = Thread4(node)
    thread5 = Thread5(node, serverip)
    thread6 = Thread6(node, serverip)
    thread7 = Thread7(node, serverip)
    thread8 = Thread8(node, serverip)
    thread9 = Thread9(node, serverip)

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
    thread6.start()
    thread7.start()
    thread8.start()
    thread9.start()


if __name__ == '__main__':
    main()
