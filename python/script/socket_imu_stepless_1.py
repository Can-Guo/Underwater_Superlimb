'''
Date: 2023-02-21 14:42:20
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-02-21 16:51:13
FilePath: /script/socket_imu_stepless_1.py
'''



# from Xbox import XBOX_Class 
from IMU_Microstrain import Microstrain_Class 
# from D435i import D435i_Class 
# from T200_Truster import POWER, T200_Class 
# from Dynamixel import Servo_Class 

import time 
import numpy as np 

from queue import Queue 
from threading import Thread 

import matplotlib.pyplot as plt

import socket as Socket
socket_IMU = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
socket_IMU.bind(("10.12.234.126", 3388))
socket_IMU.listen(10)
client_socket, clientAddr = socket_IMU.accept()


Microstrain = Microstrain_Class(SampleRate=25)
accel_enable = True; euler_enable = True
Microstrain.configIMUChannel(accel_enable,0,euler_enable)



# ## List to label the frame number
# last_frame_number =[]



def encodeIMU(IMU_Data):
    send_string = str('')
    
    send_string = str(IMU_Data[0]) + ',' + str(IMU_Data[1]) + ',' + str(IMU_Data[2]) + ',' + str(IMU_Data[3]) + ',' + str(IMU_Data[4]) + ',' + str(IMU_Data[5]) + ','
    
    print("Encoded Data: %s" % send_string)

    return send_string


def main():
    while(True):
        accel_euler_list = Microstrain.parseDataStream_Number(200, 1, accel_enable, accel_enable)
        print("Accel Euler: ", accel_euler_list)

        send_string = encodeIMU(accel_euler_list)

        client_socket.send(send_string.encode('utf-8'))

        # print("Socket: ", send_string)
        
        accel_euler_list = []

        time.sleep(0.04)


if __name__ == '__main__':
    main()
    
    

    



