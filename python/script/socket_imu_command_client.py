'''
Date: 2023-02-15 05:56:04
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-02-15 06:24:36
FilePath: /script/socket_imu_command_client.py
'''

from socket_imu_command import IMUCommandSocketClass 

Socket_Command = IMUCommandSocketClass()

msgfromClient = "Hello,UDP Server!\r\n"

serverAddressPort = ("", 54000)

while(True):

    # 1. create socekt and send a hint to client
    Socket_Command.UDPClientSocket.sendto(msgfromClient, serverAddressPort[0], serverAddressPort[1])

    msgfromServer = Socket_Command.UDPServerSocket.recvfrom(1024)

    print("IP:{},%s".format(msgfromServer[1]))

    imu_command = msgfromServer[0]
    

    # 2. get imu command signal
    

    # 3. encode 

    # 4. control the robot


