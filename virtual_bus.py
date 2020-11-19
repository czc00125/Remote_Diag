import can
import threading
import time
import random

def print_message(msg):
    print(msg)

class tx_thread_cl:

    def __init__(self, bus):
        self.bus = bus
        self.running = True
        self.thread = threading.Thread(target=self.tx_callback, args=(self.bus,))
        self.finished = False
    
    def start(self):
        self.thread.start()

    def tx_callback(self, bus):
        while self.running:
            data = [0x02, 0x10, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00]
            msg = can.Message(is_extended_id=False, arbitration_id=0x733, data=data)
            bus.send(msg)
            time.sleep(0.5)
        self.finished = True
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    # RX part
    can_interface = 'can0'
    bus_rx = can.interface.Bus(can_interface, bustype='socketcan_native')
    logger = can.Logger("logfile.asc")  # save log to asc file
    listeners = [
        print_message,  # Callback function, print the received messages
        logger,  # save received messages to asc file
    ]
    notifier = can.Notifier(bus_rx, listeners)

    # TX part
    bus_tx = can.interface.Bus(can_interface, bustype='socketcan_native')
    tx_service = tx_thread_cl(bus_tx)
    tx_service.start()

    running = True
    while running:
        input()
        running = False
    
    while not tx_service.finished:
        tx_service.stop()

    # It's important to stop the notifier in order to finish the writting of asc file
    notifier.stop()
    # stops the bus
    bus_tx.shutdown()
    bus_rx.shutdown()