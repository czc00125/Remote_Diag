import can

can_interface = 'can0'
bus = can.interface.Bus(can_interface, bustype='socketcan_native')
while True:
    message = bus.recv(10.0)  # Timeout in seconds.
    if message is None:
        print('Timeout occurred, no message.')
    print(message)
