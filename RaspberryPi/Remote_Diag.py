import threading
from threading import Thread
from time import time,sleep
import can
import random
import numpy as np
import time
import socket
from  binascii import a2b_hex,b2a_hex
from  queue import Queue
import json

can_interface = 'can0'
lock_CAN_TX = threading.Lock()
lock_CAN_RX = threading.Lock()
#use queue instead
# TCP_RX_Buff = []
TCP_TX_Buff = []
#Combine TCP TX/RX in one thread
# TCP_Connect_Flag = False
# CAN_RX_flag = False
UDS_3E_flag = False
IsCANFd_Type = False
#use event instead
# TCP_RX_flag = False

# family表示ipv6/ipv4，type表示传输协议，SOCK_STREAM表示的就是TCP协议
address = ('192.168.43.4', 9999)
UDS_RX_ID = 0x00
UDS_TX_ID = 0x00

# class MutipleThreading(threading.Thread):
#     def __init__(self, func, args=(),kwargs=None):
#         threading.Thread.__init__(self)
#         self.func = func
#         self.args = args
#         if kwargs is None:
#             kwargs = {}
#         self.kwargs = kwargs
#
#     def run(self): #override run method
#         print('{} is running'.format(self.func.__name__))
#         return self.func(self.args,**self.kwargs)
def str2hex(s):
    odata = 0
    s = str(s)
    su =s.upper()
    for c in su:
        tmp=ord(c)
        if tmp <= ord('9') :
            odata = odata << 4
            odata += tmp - ord('0')
        elif ord('A') <= tmp <= ord('F'):
            odata = odata << 4
            odata += tmp - ord('A') + 10
    return odata

def CAN_tx_service(tx_bus,Tx_q):
    print('CAN_tx_service is running')
    global UDS_RX_ID,UDS_TX_ID,UDS_3E_flag,IsCANFd_Type
    bus = tx_bus
    tx_data = []
    while True:
        event1.wait()
        # print('\n')
        data = Tx_q.get()
        # print(data[2])
        # print(type(data[2]))
        #often check type, ==1 is not true.
        tx_id = data[3:6] if int(data[2]) == 0 else data[6:9]
        UDS_3E_flag = True if int(data[1]) == 1 else False
        IsCANFd_Type = True if int(data[0]) == 1 else False
        UDS_TX_ID = str2hex(tx_id)
        UDS_RX_ID = str2hex(data[9:12])
        data = data[12:]
        for i in range(0,len(data),2):
            tx_data.append(str2hex(data[i:i+2]))
        print(len(data))
        if len(data)<16:
            for i in range(len(data),16,2):
                tx_data.append(0)
            print(tx_data)
            # data = [0x02,0x10,0x03,0x00,0x00,0x00,0x00,0x00]
            msg = can.Message(is_extended_id=IsCANFd_Type, arbitration_id=UDS_TX_ID,data=tx_data)
            tx_data.clear()
            lock_CAN_TX.acquire()
            bus.send(msg)
            # print('CAN Send Message to Radar')
            lock_CAN_TX.release()
            event1.clear()

def CAN_rx_service(rx_bus,Rx_q):
    print('CAN_rx_service is running')
    bus = rx_bus
    while True:
        # message = bus.recv(100)  # Timeout in seconds.
        message = bus.recv()  # Timeout in seconds.
        if(message.arbitration_id == UDS_RX_ID):
            # print(str2hex(str(UDS_RX_ID)))
            #Todo: parse message and then send to TCP
            # print(np.array(message.data))
            # # print(message)
            # print(type(message))
        #     lock_TCP_TX.acquire()
        #     Rx_q.put('3')
        #     event2.set()
        #     l = []
        #     l.append(message)
            print('Receive message')
            if np.array(message.data)[0] == 0x10:
                print('mutilframe')
                flow_data = [0x30,0x00,0x01,0x00,0x00,0x00,0x00,0x00]
                msg = can.Message(is_extended_id=IsCANFd_Type, arbitration_id=UDS_TX_ID, data=flow_data)
                bus.send(msg)
            Rx_q.put(str(message))
            # Rx_q.put(json.dumps(l))
            event2.set()
        elif message is None:
            print('Timeout occurred, no message.')

def TCP_service(Rx_q,Tx_q):
    print('Waiting for client connect\n')
    conn, addr = sk.accept()  # 接受TCP连接，并返回新的套接字与IP地址
    print('Connected by', addr)  # 输出客户端的IP地址
    # TCP_Connect_Flag = True
    while True:
        rx_data = conn.recv(1024)  # 把接收的数据实例化
        Rx_q.put(rx_data.decode('utf-8'))
        if rx_data !=None:
            event1.set()
        print('rx_data')
        print(rx_data)
        #Wait for 1s for CAN receive
        event2.wait(0.2)
        # if Tx_q.get() != None:
        #     tx_data = Tx_q.get()
        # else:
        #     tx_data = 'No response from target deveice'

        if (event2.isSet()):
            tx_data = Tx_q.get()
        else:
            tx_data = 'No response from target deveice'
        coded_tx_data = tx_data.encode('gbk')
        # event2.wait(0.5)
        conn.sendall(coded_tx_data)
        event2.clear()

def UDS_service():
    print('3E service is Running')
    CAN_bus = can.interface.Bus(can_interface, bustype='socketcan_native')
    bus = CAN_bus
    while True:
        data = [0x02, 0x3E, 0x80, 0x00, 0x00, 0x00, 0x00,0x00]
        if UDS_3E_flag:
            msg = can.Message(is_extended_id=IsCANFd_Type, arbitration_id=UDS_TX_ID, data=data)
            lock_CAN_TX.acquire()
            bus.send(msg)
            lock_CAN_TX.release()
            print('3E service is Running')
        sleep(2)



def print_message(msg):
    print(msg)

if __name__ == "__main__":
    logger = can.Logger("logfile.asc")  # save log to asc file
    listeners = [
        # print_message,  # Callback function, print the received messages
        logger,  # save received messages to asc file
    ]
    q1 = Queue(4096)    #used to store TCP rx message
    q2 = Queue(4096)    #used to store TCP tx message
    event1 = threading.Event()    #used for can tx
    event2 = threading.Event()    #used for TCP tx
    event3 = threading.Event()    #Used for 3E service
    # TX part
    CAN_bus = can.interface.Bus(can_interface, bustype='socketcan_native')
    notifier = can.Notifier(CAN_bus, listeners)
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # family=AF_INET, type=SOCK_STREAM socket中的两个参数，
    sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sk.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEPORT,1)
    # sk.close()
    try:
        sk.bind(address)
        # print('bind successful')
    except:
        print('cannot bind address')
    finally:
        pass
    sk.listen(3)  # 设置的是排队的个数
    print('Main thread Start')
    CAN_tx_service = Thread(target = CAN_tx_service,args=(CAN_bus,q1) )
    CAN_rx_service = Thread(target = CAN_rx_service,args=(CAN_bus,q2) )
    TCP_service = Thread(target = TCP_service,args=(q1,q2))
    UDS_service = Thread(target = UDS_service, args=())

    CAN_tx_service.setDaemon(True)
    CAN_rx_service.setDaemon(True)
    TCP_service.setDaemon(True)
    UDS_service.setDaemon(True)

    CAN_tx_service.start()
    CAN_rx_service.start()
    UDS_service.start()
    TCP_service.start()

    CAN_tx_service.join()
    CAN_rx_service.join()
    UDS_service.join()
    TCP_service.join()
    sk.close()
    print('Main thread End')
