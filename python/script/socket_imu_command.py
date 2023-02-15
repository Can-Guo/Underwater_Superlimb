'''
Date: 2023-02-15 05:55:35
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-02-15 07:17:21
FilePath: /script/socket_imu_command.py
'''


import socket 

# import os 
# import csv


class IMUCommandSocketClass(object):

    def __init__(self, local_ip="10.12.234.126", local_port=54000, server_or=1):
        
        self.serverAddressPort = (local_ip, local_port)

        try:
            self.UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            if server_or == 1:
                self.UDPServerSocket.bind((local_ip, local_port))
                print("Socket Server Initialization is Successfyl!\r\n")
            elif server_or == 0:
                print("Socket Client Initialization is Successfyl!\r\n")

        except:
            print("UDP Initialization Failed! Please check your ip and port!\r\n")
    
    
