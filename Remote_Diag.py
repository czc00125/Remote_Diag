import threading
from time import time,sleep
import can
import random
import numpy as np
import time

can_interface = 'can0'
lock_CAN_TX = threading.Lock()
lock_TCP_TX = threading.Lock()
TCP_RX_Buff = []
TCP_TX_Buff = []
class MutipleThreading(threading.Thread):
    def __init__(self, func, args=(),kwargs=None):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        if kwargs is None:
            kwargs = {}
        self.kwargs = kwargs

    def run(self): #override run method
        print('{} is running'.format(self.func.__name__))
        return self.func(self.args,**self.kwargs)

def CAN_tx_service(tx_bus):
        bus = tx_bus
        while True:
            # data = [0x02,0x10,0x03,0x00,0x00,0x00,0x00,0x00]
            msg = can.Message(is_extended_id=False, arbitration_id=0x733,data=TCP_RX_Buff)
            bus.send(msg)
            sleep(0.5)


def CAN_rx_service(rx_bus):
    global TCP_TX_Buff
    bus = rx_bus
    while True:
        message = bus.recv(1)  # Timeout in seconds.
        if message is None:
            print('Timeout occurred, no message.')
        elif(message.arbitration_id != 0x73B):
            #Todo: parse message and then send to TCP
            print(np.array(message.data))
            lock_TCP_TX.acquire()
            TCP_TX_Buff.append(message)
            lock_TCP_TX.release()
        sleep(1)

def TCP_rx_service(TCP):
    global TCP_RX_Buff
    while True:
        print('TCP RX service is running\n')
        lock_CAN_TX.acquire()
        #Todo:parse TCP message, and then update buff
        TCP_RX_Buff = [random.randint(0,15) for i in range(0,8)]
        lock_CAN_TX.release()
        sleep(1)

def TCP_tx_service(TCP):
    while True:
        print('TCP TX service is running\n')
        print(TCP_TX_Buff)
        sleep(1)

def print_message(msg):
    print(msg)

if __name__ == "__main__":
    logger = can.Logger("logfile.asc")  # save log to asc file
    listeners = [
        # print_message,  # Callback function, print the received messages
        logger,  # save received messages to asc file
    ]
    # TX part
    CAN_bus = can.interface.Bus(can_interface, bustype='socketcan_native')
    notifier = can.Notifier(CAN_bus, listeners)
    print('Main thread Start')
    CAN_tx_service = MutipleThreading(CAN_tx_service,args=(CAN_bus))
    CAN_rx_service = MutipleThreading(CAN_rx_service,args=(CAN_bus))
    TCP_rx_service = MutipleThreading(TCP_rx_service,args=())
    TCP_tx_service = MutipleThreading(TCP_tx_service,args=())

    CAN_tx_service.setDaemon(True)
    CAN_rx_service.setDaemon(True)
    TCP_rx_service.setDaemon(True)
    TCP_tx_service.setDaemon(True)

    CAN_tx_service.start()
    CAN_rx_service.start()
    TCP_rx_service.start()
    TCP_tx_service.start()
    CAN_tx_service.join()
    CAN_rx_service.join()
    TCP_rx_service.join()
    TCP_tx_service.join()
    print('Main thread End')
