'''
Date: 2023-02-15 05:56:04
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-02-15 06:18:09
FilePath: /script/socket_imu_command_server.py
'''

from socket_imu_command import IMUCommandSocketClass 

Socket_Command = IMUCommandSocketClass()

while(True):
    # 1. create socekt and send a hint to client
    Data = Socket_Command.UDPServerSocket.recvfrom(1024)

    # 2. generate imu command signal


    # 3. send to client, raspberrypi 4B
