'''
Date: 2023-03-23 11:22:07
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-23 15:49:08
FilePath: /script/run_robot_yaw_PID.py
'''


import os
import csv
from datetime import datetime

from Xbox import XBOX_Class 
from IMU_Microstrain import Microstrain_Class 
from T200_Truster import POWER, T200_Class 
from Dynamixel import Servo_Class 

import time 
import numpy as np 

from queue import Queue 
from threading import Thread 
import matplotlib.pyplot as plt 


# import socket as Socket 
## TCP Server: Raspberry Pi
# ip = "10.42.0.108"
# port = 5555
# s= Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM) 
# s.bind((ip, port)) 
# s.listen(10) 
# client_socket, clienttAddr=s.accept() 


## initial the control library of T200 Thruster
T200 = T200_Class() 
T200.T200_power_scale = POWER[1] 
T200.send_T200_PWM_Width([1500, 1500]) 
print("Initilize the T200 ...") 


## initial the control SDK of Dynamixel XW540-T140-R servo
PortName = '/dev/ttyUSB0'
Servo = Servo_Class(PortName, 57600)                             
Servo.enable_Torque()
time.sleep(0.5)
Servo.sync_Write_Angle([0,0])
print("Initialize the T200 and Servo is Successful!")



## Function to create a data logger as CSV file

def creatLogcsv():
    cwd = os.path.abspath('.')
    time_mark = datetime.now()
    
    file_name = str(cwd) + '/servo_thruster_data_0323/' + str(time_mark) + '_yaw_PID.csv'

    print("Path to log data:", file_name)

    with open(file_name,'a') as file:
        writer = csv.writer(file,delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Timestamp_log','left_angle','right_angle','left_thrust',
                         'right_thrust','read_left_angle','read_right_angle',
                         'accel_x','accel_y','accel_z','roll','pitch','yaw','e_alpha'])

    file.close()

    return file_name 


## Function to encode IMU data into string to be sent

# def encode_imu_to_str(imu_list):

#     send_string = str('')
#     for data in imu_list:
#         send_string = send_string + str(data) + ','
    
#     send_string = send_string + '#'

#     print("Encode Data: %s" % send_string)

#     return send_string 



def main(yaw_exp):

    # 0. Create a CSV file to record imu data
    csv_file_name = creatLogcsv()

    # 1.1 Enable IMU 
    accel_enable = True 
    euler_enable = True 
    IMU = Microstrain_Class()
    IMU.configIMUChannel(accel_enable,0,euler_enable) 
    
    roll_0_list = []
    pitch_0_list = []
    yaw_0_list = []

    # 1.2 Calibration of the IMU data of the initial status
    for i in range(500):
        imu_data_calibration = IMU.parseDataStream_Number(200,1, accel_enable, euler_enable)
        roll_0_list.append(imu_data_calibration[3])
        pitch_0_list.append(imu_data_calibration[4])
        yaw_0_list.append(imu_data_calibration[5])

    roll_0 = np.mean(roll_0_list)
    pitch_0 = np.mean(pitch_0_list)
    yaw_0 = np.mean(yaw_0_list)

    Yaw_Expectation = yaw_0 + yaw_exp
    ## initial the yaw error
    yaw_error_last = Yaw_Expectation
    print('------------------------------------------------')
    print("Calibration of the IMU data is done!\r\n")

    i = 0
    K_p = 25
    K_d = 0.1
    
    left_angle = 0
    right_angle = 0
    left_thrust = 1500
    right_thrust = 1500

    while True:
        # 2. Access the imu data and time stamp
        imu_data = IMU.parseDataStream_Number(200, 1, accel_enable, euler_enable) 
        
        time_stamp = datetime.now() 
        time_stamp = time_stamp.strftime("%Y-%m-%d %H-%M-%S-%f") 

        # 3. Calculate the error of the yaw angle
        yaw_error = Yaw_Expectation - imu_data[5] 

        # 4.1 Calculate the Control command according to the Euler angle from IMU sensor 
        delta_Thrust = K_p * yaw_error + K_d * (yaw_error - yaw_error_last)

        right_thrust = 1475
        left_thrust = right_thrust + delta_Thrust

        # 4.2 Check the control command of the Thruster
        if left_thrust < 1450:
            left_thrust = 1450
        elif left_thrust > 1550:
            left_thrust = 1550
        
        if right_thrust < 1450:
            right_thrust = 1450
        elif right_thrust > 1550:
            right_thrust = 1550

        # 4.3 Send control command to servos and thrusters
        T200.send_T200_PWM_Width([left_thrust,right_thrust])
        
        # 5.1 Read the servo angle 
        read_servo_angle = Servo.sync_Read_Angle()
        # 5.2 Save the imu data and control command 
        with open(csv_file_name,'a') as file:
            writer = csv.DictWriter(file, fieldnames=[])
            writer.writerow({'Timestamp_log':time_stamp,'left_angle':left_angle,'right_angle':right_angle,'left_thrust':left_thrust,
                         'right_thrust':right_thrust,'read_left_angle':read_servo_angle[0],'read_right_angle':read_servo_angle[1],
                         'accel_x':imu_data[0],'accel_y':imu_data[1],'accel_z':imu_data[2],'roll':imu_data[3],'pitch':imu_data[4],'yaw':imu_data[5],'e_alpha':yaw_error})
        print()
        # 6. update the last frame of the error of the yaw angle

        yaw_error_last = yaw_error 

        i += 1
        
        if i>= 1000:
            # stop the thruster 
            T200.send_T200_PWM_Width([1500,1500])
            Servo.disable_Torque()

            exit()


if __name__ == '__main__':

    main(yaw_exp=45.0)

    pass 
