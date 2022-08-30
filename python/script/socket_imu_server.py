'''
Date: 2022-08-27 00:44:09
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-30 21:58:21
FilePath: \script\socket_imu_server.py
'''


import socket


class IMUSocketClass(object):

    def __init__(self, local_ip="169.254.10.50", local_port=54000):
        

        
        # msgFromServer       = "Hello UDP Client!".encode('utf-8')

        try:
            self.UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDPServerSocket.bind((local_ip, local_port))

        except:

            print("UDP Initialization Failed! Please check your ip and port!\r\n")


    ## Get the data and send to other computer.
    
    def sendback_imu_data(self):

        # 3. formate the imu data

        # 4. send back to PC or Ubuntu


        return
    
    
    ## 

    def encode_imu_data_to_str(self, number_list):
        

        return 


    ## imu data as string, convert into number list

    def decode_imu_data_to_list(self, recv_string):

        print(recv_string)
        
        return 


    def createCSV(self):
        
        return 

    
    


########################################################
# Test this Module

# localIP   =  "169.254.10.50"
# localPort   = 54000

IMUSocket = IMUSocketClass() #localIP,localPort)

IMUSocket

print("UDP Server Communication Begin!")

while(True):
    Data = UDPServerSocket.recvfrom(1024)

    # print("Client IP Address:{}".format(Data[1]))
    # print("Message from Client:{}".format(Data[0].decode('gbk')))
    
    UDPServerSocket.sendto(msgFromServer, Data[1])

    # UDPServerSocket.close()

# Testing End
########################################################
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  