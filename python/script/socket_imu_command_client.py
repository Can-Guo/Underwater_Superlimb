'''
Date: 2023-02-15 05:56:04
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-02-16 00:49:22
FilePath: /script/socket_imu_command_client.py
'''

from socket import socket
import socket as Socket
from socket_imu_command import IMUCommandSocketClass 

# Socket_Command = IMUCommandSocketClass()

# msgfromClient = "Hello,UDP Server!".encode('utf-8')

# serverAddressPort = ("10.12.234.126", 54000)

s=Socket.socket(Socket.AF_INET,Socket.SOCK_STREAM)
#连接服务器
# s.connect(("192.168.137.1",7788))
s.connect(("10.13.228.137", 7788))


while(True):
    ##TCP连接发送语音设别信息的PC端，客户端不发送任何数据，只作为信息的接收方即可
    ##
    recvData=s.recv(1024)

    print( "收到的数据为：",recvData.decode("utf-8"))
    
    # # 1. create socekt and send a hint to client
    # Socket_Command.UDPClientSocket.sendto(msgfromClient, serverAddressPort)

    # msgfromServer = Socket_Command.UDPClientSocket.recvfrom(1024)

    # # print("IP:{}".format(msgfromServer[1]))

    # # print("IMU command %s", msgfromServer[0])

    # imu_command = msgfromServer[0].decode('utf-8')

    # print(imu_command)


    # 2. get imu command signal
    

    # 3. encode 

    # 4. control the robot


