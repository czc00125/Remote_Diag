#!/usr/bin/python
import socket

sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    # family=AF_INET, type=SOCK_STREAM socket中的两个参数，
# family表示ipv6/ipv4，type表示传输协议，SOCK_STREAM表示的就是TCP协议

address = ('192.168.43.4', 9999)
# address = ('175.24.119.43', 9999)

sk.bind(address)

sk.listen(3)  # 设置的是排队的个数
print('Waiting.......')
while 1:
        conn, addr = sk.accept()  # 接受TCP连接，并返回新的套接字与IP地址
        print('Connected by', addr)    #输出客户端的IP地址
        while 1:
            rx_data = conn.recv(1024)    #把接收的数据实例化
            print('Receive data: ', rx_data)
            tx_data = input('send message:')
            coded_tx_data = tx_data.encode('gbk')
            conn.sendall(coded_tx_data)
sk.close()
