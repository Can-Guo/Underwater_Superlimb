'''
Date: 2023-02-15 05:56:04
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-02-15 07:33:27
FilePath: /script/socket_imu_command_client.py
'''

from socket_imu_command import IMUCommandSocketClass 

Socket_Command = IMUCommandSocketClass()

msgfromClient = "Hello,UDP Server!".encode('utf-8')

serverAddressPort = ("10.12.234.126", 54000)

while(True):

    # 1. create socekt and send a hint to client
    Socket_Command.UDPClientSocket.sendto(msgfromClient, serverAddressPort)

    msgfromServer = Socket_Command.UDPClientSocket.recvfrom(1024)

    # print("IP:{}".format(msgfromServer[1]))

    # print("IMU command %s", msgfromServer[0])

    imu_command = msgfromServer[0].decode('utf-8')

    print(imu_command)


    # 2. get imu command signal
    

    # 3. encode 

    # 4. control the robot


