'''
Date: 2022-08-27 00:44:09
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-30 23:24:56
FilePath: /script/socket_imu_server.py
'''


import socket


from datetime import datetime 
import os 
import csv 
import platform

import IMU_Microstrain 
from IMU_Microstrain import Microstrain_Class 


## Differ the system platform for different file path system
if platform.system().lower() == 'windows':
    print("当前的操作系统是windows")
    sys_platform = 'windows'
elif platform.system().lower() == 'linux':
    print("当前的操作系统是linux")
    sys_platform = 'linux'

# print(sys_platform)



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
        send_string = str('')
        for data in number_list:
            send_string = send_string + str(data) + ','

        print("Send Data: %s",send_string)

        return send_string


    ## imu data as string, convert into number list

    def decode_imu_data_to_list(self, recv_string):

        print(recv_string)
        
        return 


    def create_csv(self):
        cwd = os.path.abspath('.')
        cwd = os.path.dirname(cwd)

        time_mark = datetime.now()

        time_mark = time_mark.strftime("%Y-%m-%d %H-%M-%S")
        if sys_platform == 'windows':
            file_name = str(cwd) + '\csv\imu_data_' + str(time_mark) + '_save.csv'
        elif sys_platform == 'linux':
            file_name = str(cwd) + '/csv/imu_data_' + str(time_mark) + '_save.csv'

        # print(file_name)

        with open(file_name, 'a') as file:
            writer = csv.writer(file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
            writer.writerow(['Timestamp', 'Accel_x', 'Accel_y', 'Accel_z', 'Roll', 'Pitch', 'Yaw'])

        file.close()

        return file_name

    

########################################################
# Test this Module

# 1. initialize the SOCKET UDP communication
# localIP   =  "169.254.10.50"
# localPort   = 54000

IMUSocket = IMUSocketClass() #localIP,localPort)

# 2. initialize the Microstrain IMU for data streaming
Microstrain_IMU = Microstrain_Class(SampleRate=100)
accel_enable = True; euler_enable = True
Microstrain_IMU.configIMUChannel(accel_enable,0,euler_enable)

# 3. create a CSV file for data collection
filename = IMUSocket.create_csv()
imu_data_frame = Microstrain_IMU.parseDataStream_Number(100,1,accel_enable,euler_enable)

Send_String = IMUSocket.encode_imu_data_to_str(imu_data_frame)
Send_String = Send_String.encode('utf-8')

print("UDP Server Communication Begin!")

while(True):

    Data = IMUSocket.UDPServerSocket.recvfrom(1024)

    print("Client IP Address:{}".format(Data[1]))
    print("Message from Client:{}".format(Data[0].decode('gbk')))
    
    IMUSocket.UDPServerSocket.sendto(Send_String, Data[1])

IMUSocket.UDPServerSocket.close()

# Testing End
########################################################
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  