'''
Date: 2023-02-21 14:26:07
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-14 11:46:09
FilePath: /script/run_robot_double_stepless_1_exp_1.py
'''

import csv
from datetime import datetime 
import os 

from T200_Truster import POWER, T200_Class 
from Dynamixel import Servo_Class 
import time 
import socket as Socket


# # initial the control library of T200 Thruster
T200_thruster = T200_Class()
T200_thruster.T200_power_scale = POWER[1]
T200_thruster.send_T200_PWM_Width([1500, 1500])
print("Initilize the T200 ...")


# # initial the control SDK of Dynamixel XW540-T140-R servo
PortName = '/dev/ttyUSB0'
Servo = Servo_Class(PortName, 57600)                             
Servo.enable_Torque()
Servo.sync_Write_Angle([0,0])
time.sleep(0.5)

print("Initialize the T200 and Servo is Successful!")


## 1. initialize the UDP communication 
port = 3300
socket_pi = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
socket_pi.settimeout(5000)
socket_pi.connect(("10.12.234.126",port))


def creatLogcsv():
    cwd = os.path.abspath('.')
    time_mark = datetime.now()
    
    file_name = str(cwd) + '/servo_thruster_data_0311/' + str(time_mark) + '.csv'

    print("Path to log data:", file_name)

    with open(file_name,'a') as file:
        writer = csv.writer(file,delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Timestamp_log','left_angle','right_angle','left_thrust','right_thrust','read_left_angle','read_right_angle'])

    file.close()

    return file_name 


def decodeClient(Data_Server):

    mode_euler_lists = Data_Server.split('!')

    mode_euler_list_first = mode_euler_lists[0].split(',')

    # print("Decoded Data List", mode_euler_list_first)

    return mode_euler_list_first 


def T200_Servo_command():
    
    print("Begin Servo and Thruster Control!\r\n")

    i = 0

    left_angle = 0
    right_angle = 0
    left_thrust = 1500
    right_thrust = 1500

    K_1 = 2.0
    K_2 = 2.0

    K_3 = 1.0*1.5
    K_4 = 2.0*1.5

    K_5 = 2.0
    K_6 = 2.0

    next_mode = 0


    msgFromServer = socket_pi.recv(1024)
    Decoded_mode_euler_List = decodeClient(msgFromServer.decode('utf-8'))
    
    if(len(Decoded_mode_euler_List)<=3):
        pass
    else:
        roll_calib = round(float(Decoded_mode_euler_List[1]),2)
        pitch_calib = round(float(Decoded_mode_euler_List[2]),2)
        yaw_calib = round(float(Decoded_mode_euler_List[3]),2)
    
        print("Roll: %.2f Pitch: %.2f Yaw: %.2f" % (roll_calib, pitch_calib, yaw_calib))

    csv_log_file = creatLogcsv()

    while(i<=1000):

        msgFromServer = socket_pi.recv(1024)
        Decoded_mode_euler_List = decodeClient(msgFromServer.decode('utf-8'))

        if(len(Decoded_mode_euler_List)<=3):
            pass
        else:

            # print("From Server:",Decoded_mode_euler_List)
            next_mode = int(Decoded_mode_euler_List[0])
            roll_delta = round(float(Decoded_mode_euler_List[1]),2)
            pitch_delta = round(float(Decoded_mode_euler_List[2]),2)
            yaw_delta = round(float(Decoded_mode_euler_List[3]),2)
            
            print("Next_Mode: %d \t Roll_d: %.2f Pitch_d: %.2f Yaw_d: %.2f" % (next_mode ,roll_delta, pitch_delta, yaw_delta))

        if next_mode==0:
            left_angle =0
            right_angle=0
            left_thrust=1500
            right_thrust=1500

        if next_mode==2:
            left_angle = (int)(K_2 * (int)(pitch_delta-20))
            right_angle = (int)(left_angle)
            pass

        if next_mode==1:
            left_angle = (int)(K_1 * (int)(pitch_delta+20))
            right_angle = (int)(left_angle)

            pass

        if next_mode==5:
            left_angle = (int)(K_5 * (int)(yaw_delta+20))
            right_angle = - (int)(left_angle)

        if next_mode==6:
            left_angle = (int)(K_6 * (int)(yaw_delta-20))
            right_angle = - (int)(left_angle)


        if next_mode==3:
            left_thrust = 1500 + K_3*(int)(roll_delta-20)
            right_thrust= left_thrust
            left_angle = -90
            right_angle= -90

        if next_mode==4:
            left_thrust = 1500 + K_4*(int)(roll_delta+20) 
            right_thrust = left_thrust
            left_angle = -90
            right_angle= -90

        
        
        ## send command to servo and thruster
        pass 
        
        if left_thrust>=1600:
            left_thrust=1600
        elif left_thrust<=1400:
            left_thrust=1400
        
        if right_thrust>=1600:
            right_thrust=1600
        elif right_thrust<=1400:
            right_thrust=1400

        print("Left_Angle:%d Right_Angle:%d Left_Thrust:%d Right_Thrust:%d" % (left_angle,right_angle,left_thrust,right_thrust))    
        Servo.sync_Write_Angle([left_angle,right_angle])
        T200_thruster.send_T200_PWM_Width([left_thrust,right_thrust])
        
        current_time = datetime.now()
        read_servo_angle_list = Servo.sync_Read_Angle()

        with open(csv_log_file,'a') as file:
            writer = csv.DictWriter(file, fieldnames=['Timestamp_log','left_angle','right_angle','left_thrust','right_thrust','read_left_angle','read_right_angle']
            'left_thrust':left_thrust,'right_thrust':right_thrust,'read_left_angle':read_servo_angle_list[0],'read_right_angle':read_servo_angle_list[1]})
        # time.sleep(0.001)

        file.close() 

if __name__ == '__main__':
    T200_Servo_command()


