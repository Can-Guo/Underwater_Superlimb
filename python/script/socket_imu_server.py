'''
Date: 2022-08-27 00:44:09
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-27 19:50:18
FilePath: /script/socket_imu_server.py
'''


import socket
localIP   =  "169.254.10.50"
localPort   = 54000
msgFromServer       = "Hello UDP Client!".encode('utf-8')

UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPort))
print("UDP server begin!")

while(True):
    Data = UDPServerSocket.recvfrom(1024)
    print("Client IP Address:{}".format(Data[1]))
    print("Message from Client:{}".format(Data[0]))
    
    UDPServerSocket.sendto(msgFromServer, Data[1])
                                                                                                                                                                                                                                                                                                           
    # UDPServerSocket.close()

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  