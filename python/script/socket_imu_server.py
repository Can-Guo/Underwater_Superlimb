'''
Date: 2022-08-27 00:44:09
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-09-01 16:57:55
FilePath: /script/socket_imu_server.py
'''

# import socket 
import Socket_IMU 

from Socket_IMU import IMUSocketClass 
from IMU_Microstrain import Microstrain_Class 
from datetime import datetime 

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

# 3. create a CSV file for data collection at client
# filename = IMUSocket.create_csv()

print("UDP Server Communication Begin!")

while(True):

    Data = IMUSocket.UDPServerSocket.recvfrom(1024)
    
    imu_data_frame = Microstrain_IMU.parseDataStream_Number(100,1,accel_enable,euler_enable)

    time_stamp = datetime.now()
    time_stamp = time_stamp.strftime("%Y-%m-%d %H-%M-%S-%f")

    imu_data_frame.append(time_stamp)
    
    Send_String = IMUSocket.encode_imu_data_to_str(imu_data_frame)
    Send_String = Send_String.encode('utf-8')

    print("Client IP Address:{}".format(Data[1]))
    print("Message from Client:{}".format(Data[0].decode('gbk')))
    
    IMUSocket.UDPServerSocket.sendto(Send_String, Data[1])

IMUSocket.UDPServerSocket.close()

# Testing End
########################################################
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  