'''
Date: 2022-11-14 06:40:12
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-11-14 16:28:24
FilePath: \script\Socket_Mi.py
'''

import socket 
import platform

from datetime import datetime 
import os 
import numpy as np 
import matplotlib.pyplot as plt 

## Differ the system platform for different file path system
if platform.system().lower() == 'windows':
    print("当前的操作系统是windows")
    sys_platform = 'windows'
elif platform.system().lower() == 'linux':
    print("当前的操作系统是linux")
    sys_platform = 'linux'


class MiSocketClass(object):

    def __init__(self, local_ip="169.254.10.50", local_port=82000, server_or = 1):
        self.serverAddressPort = (local_ip, local_port)
        self.msgFromClient = "Hello, UDP Server. This is Client from PC!".encode('utf-8')
        
        try:
            self.UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            if server_or == 1:
                self.UDPClientSocket.bind((local_ip, local_port))
                print("Microphone Socket Server Initialization is Successful!\r\n")
            elif server_or == 0:
                print("Microphone Socket Client Initialization is Successful!\r\n")
            
        except:
            print("IMU UDP Initialization Failed! Please check your ip and port!\r\n")
        

    
