'''
Date: 2023-04-17 14:14:24
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-04-19 10:47:26
FilePath: /script/run_robot_spherical_coord.py
'''


import os
import csv
from datetime import datetime

# from Xbox import XBOX_Class 
# from IMU_Microstrain import Microstrain_Class 
from T200_Truster import POWER, T200_Class 
from Dynamixel import Servo_Class 

import time 
import numpy as np 
import socket as Socket


## 1. initialize the TCP communication 
port = 8888
socket_pi = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
socket_pi.settimeout(5000)
socket_pi.connect(("10.24.24.199",port))


## 2. initial the control library of T200 Thruster
T200 = T200_Class() 
T200.T200_power_scale = POWER[1] 
T200.send_T200_PWM_Width([1500, 1500]) 
print("Initilize the T200 ...") 


## 3. initial the control SDK of Dynamixel XW540-T140-R servo
left_angle_init = -90
right_angle_init = -110

PortName = '/dev/ttyUSB0'
Servo = Servo_Class(PortName, 57600)                             
Servo.enable_Torque()
time.sleep(1.0)
Servo.sync_Write_Angle([left_angle_init,right_angle_init])
time.sleep(1.0)
Servo.disable_Torque()

print("Initialize the T200 and Servo is Successful!")


def decode_imu_data(Data_Server):

    imu_frame = Data_Server.split('!')
    imu_data_list = imu_frame[-1].split(',')
    print("Data Decoded:", imu_data_list)


## Function to create a data logger as CSV file

def creatLogcsv():
    cwd = os.path.abspath('.')
    time_mark = datetime.now()
    
    file_name = str(cwd) + '/servo_thruster_data_0417/' + str(time_mark) + '_spherical_PD.csv'

    print("Path to log data:", file_name)

    with open(file_name,'a') as file:
        writer = csv.writer(file,delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Timestamp_log','left_angle','right_angle','left_thrust',
                         'right_thrust','read_left_angle','read_right_angle',
                         'accel_x','accel_y','accel_z','roll','pitch','yaw','error'])

    file.close()

    return file_name 


## Main Function
def main(angle_expected):
    csv_file_name = creatLogcsv()
    roll_0_list = []
    pitch_0_list = []
    yaw_0_list = []

    # 4.1 Calibration of the IMU data of the initial status
    for i in range(100):
        ## receive the imu data from IMU device (@Ubuntu PC)
        msgFromServer = socket_pi.recv(1024)
        imu_data_calibration = decode_imu_data(msgFromServer.decode('utf-8'))

        roll_0_list.append(imu_data_calibration[3])
        pitch_0_list.append(imu_data_calibration[4])
        yaw_0_list.append(imu_data_calibration[5])
        

    roll_0 = np.mean(roll_0_list)
    pitch_0 = np.mean(pitch_0_list)
    yaw_0 = np.mean(yaw_0_list)
    
    print("Calibration Result:", roll_0, pitch_0, yaw_0)
    print('------------------------------------------------')
    print("Calibration of the IMU data is done!\r\n")
    
    ## initial the angle error
    angle_error = angle_expected

    i = 0
    K_p = 1.0
    K_d = 0.2
    left_angle = 0
    right_angle = 0
    left_thrust = 1500
    right_thrust = 1500 

    # start = time.time()

    while(True):
        start = time.time()
        ## receive the imu data from IMU device (@Ubuntu PC)
        msgFromServer = socket_pi.recv(1024)
        imu_data_lastest = decode_imu_data(msgFromServer.decode('utf-8'))

        angle_error = -(imu_data_lastest[4] - angle_expected)

        # time stamp access
        time_stamp = datetime.now() 
        time_stamp = time_stamp.strftime("%Y-%m-%d %H-%M-%S-%f") 

        # 4.2 Calculate the PWM value of the Thrusters based on the IMU data feedback
        # T200.send_T200_PWM_Width([1500,1500])
        time.sleep(0.05)

        delta_Thrust = K_p * angle_error + K_d * (angle_error - angle_error_last)

        if (angle_error>0):
    
            right_thrust = right_thrust_last + (int)(delta_Thrust) 
            left_thrust  = left_thrust_last + (int)(delta_Thrust)

            if(np.abs(angle_error)<2):
                left_thrust = left_thrust_last
                right_thrust = right_thrust_last

        elif(angle_error<0):
            right_thrust = right_thrust_last - (int)(delta_Thrust) 
            left_thrust  = left_thrust_last - (int)(delta_Thrust)

            if(np.abs(angle_error)<2):
                left_thrust = left_thrust_last
                right_thrust = right_thrust_last
                
        print("angle_error %f, Delta_thrust %f.")

        # 4.3 Check the control of the Thruster
        MIN = 1430
        MAX = 1570

        if left_thrust <= MIN:
            left_thrust = MIN
        elif left_thrust >= MAX:
            left_thrust = MAX
        
        if right_thrust <= MIN:
            right_thrust = MIN
        elif right_thrust >= MAX:
            right_thrust = MAX

        # 4.4 Send control command to servos and thrusters
        T200.send_T200_PWM_Width([(int)(left_thrust),(int)(right_thrust)])
        
        read_servo_angle = Servo.sync_Read_Angle()

        # 5.1 Save the imu data and control command 
        with open(csv_file_name,'a') as file:
            writer = csv.DictWriter(file, fieldnames=['Timestamp_log','left_angle','right_angle','left_thrust',
                         'right_thrust','read_left_angle','read_right_angle',
                         'accel_x','accel_y','accel_z','roll','pitch','yaw','error'])
            writer.writerow({'Timestamp_log':time_stamp,'left_angle':left_angle,'right_angle':right_angle,'left_thrust':left_thrust,
                         'right_thrust':right_thrust,'read_left_angle':read_servo_angle[0],'read_right_angle':read_servo_angle[1],
                         'accel_x':imu_data_lastest[0],'accel_y':imu_data_lastest[1],'accel_z':imu_data_lastest[2],'roll':imu_data_lastest[3],'pitch':imu_data_lastest[4],'yaw':imu_data_lastest[5],'error':angle_error})
        
        print("==>%s, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f" %
        (str(time_stamp),left_angle,right_angle,left_thrust,right_thrust,read_servo_angle[0],read_servo_angle[1],
        imu_data_lastest[0],imu_data_lastest[1],imu_data_lastest[2],imu_data_lastest[3],imu_data_lastest[4],imu_data_lastest[5],angle_error))

        # 6. update the last frame of the error of the yaw angle
        angle_error_last = angle_error 
        left_thrust_last = left_thrust
        right_thrust_last = right_thrust

        # exit for over time

        i += 1

        if i>= 150:
            T200.send_T200_PWM_Width([1500,1500])
            exit()
        
        if(time.time()-start>10):
            T200.send_T200_PWM_Width([1500,1500])
            exit()


if __name__ == '__main__':
    
    angle_exp = 30
    main(angle_expected=angle_exp)



