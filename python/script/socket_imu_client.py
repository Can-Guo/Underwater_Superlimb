'''
Date: 2022-08-27 22:00:19
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-30 23:26:13
FilePath: \script\socket_imu_client.py
'''

# '''
# Date: 2022-08-27 16:18:18
# LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
# LastEditTime: 2022-08-27 16:20:20
# FilePath: \Underwater_Client\socket_imu_client.py
# '''

import socket
import time 

msgFromClient       = "Hello UDP Server,This is Client from PC!".encode('utf-8')
serverAddressPort   = ("169.254.10.50", 54000)

UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    UDPClientSocket.sendto(msgFromClient, serverAddressPort)

    msgFromServer = UDPClientSocket.recvfrom(1024)

    print("Server IP Address:{}", msgFromServer[1])
    print(format(msgFromServer[0].decode('gbk')))

    time.sleep(1)

    # UDPClientSocket.close()


