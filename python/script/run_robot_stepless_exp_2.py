'''
Date: 2023-03-12 00:35:49
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-14 20:45:53
FilePath: /script/run_robot_stepless_exp_2.py
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
port = 3344
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

    mode_strength = Data_Server.split('!')

    mode_strength_first = mode_strength[0].split(',')

    return mode_strength_first 


def T200_Servo_command():
    
    print("Begin Servo and Thruster Control!\r\n")

    i = 0

    left_angle = 0
    right_angle = 0
    left_thrust = 1500
    right_thrust = 1500

    K_1 = 20.0
    K_2 = -20.0

    K_3 = 25.0
    K_4 = -25.0

    K_5 = 20.0
    K_6 = -20.0

    # K_7 = 25.0
    # K_8 = -25.0

    flag = 0

    csv_log_file = creatLogcsv()

    while(i<=1000):

        msgFromServer = socket_pi.recv(1024)
        Decoded_mode_strength_first = decodeClient(msgFromServer.decode('utf-8'))

        if(len(Decoded_mode_strength_first)<2):
            flag = 0

        else:
            if(len(Decoded_mode_strength_first)<2):
                flag = 0
            else:
                print("From Server:",Decoded_mode_strength_first)
                
            if Decoded_mode_strength_first[0]=='do' and Decoded_mode_strength_first[1] =='S':
                flag = 2
                print("Voice is do S!")
                
            elif Decoded_mode_strength_first[0]=='do' and Decoded_mode_strength_first[1] =='L':
                flag = 1
                print("Voice is do L!")
            elif Decoded_mode_strength_first[0]=='re' and Decoded_mode_strength_first[1] =='S':
                flag = 6
                print("Voice is re S!")
            elif Decoded_mode_strength_first[0]=='re' and Decoded_mode_strength_first[1] =='L':
                flag = 5
                print("Voice is re L!")
            elif Decoded_mode_strength_first[0]=='me' and Decoded_mode_strength_first[1] =='S':
                flag = 3
                print("Voice is me S!")
            elif Decoded_mode_strength_first[0]=='me' and Decoded_mode_strength_first[1] =='L':
                flag = 4
                print("Voice is me L!")

            # elif Decoded_mode_strength_first[0]=='fa':
            #     flag = 7
            #     print("Voice is fa !")
            # elif Decoded_mode_strength_first[0]=='so':
            #     flag = 8
            #     print("Voice is so !")

            elif Decoded_mode_strength_first[1]=='T':
                strength = float(Decoded_mode_strength_first[0])

                if flag==2:
                    left_angle = (int)(K_2 * strength)
                    right_angle = (int)(left_angle)

                elif flag==1:
                    left_angle = (int)(K_1 * strength)
                    right_angle = (int)(left_angle)

                elif flag==6:
                    left_angle = (int)(K_6 *  strength)
                    right_angle = - (int)(left_angle)

                elif flag==5:
                    left_angle = (int)(K_5 * strength)
                    right_angle = - (int)(left_angle)

                elif flag==3:
                    left_thrust = 1500 + (int)(K_3 * strength)
                    right_thrust = left_thrust
                    left_angle = -90
                    right_angle= -90

                elif flag==4:
                    left_thrust = 1500 + (int)(K_4 * strength)
                    right_thrust = left_thrust
                    left_angle = -90
                    right_angle= -90

                # if flag==7:
                #     left_thrust = 1500 + K_7 * 
                #     right_thrust = left_thrust
                #     left_angle = -90
                #     right_angle= -90

                # if flag==8:
                #     left_thrust = 1500 + K_8 * 
                #     right_thrust = left_thrust
                #     left_angle = -90
                #     right_angle= -90
            elif Decoded_mode_strength_first[1]=='Q':
                flag = 0
                print("Accepted Reset Command:Q!\r\n")

        if flag == 0:
            left_angle =0
            right_angle=0
            left_thrust=1500
            right_thrust=1500
            print("Reset to Home Position!\r\n")

        ## send command to servo and thruster
        
        if left_thrust>=1600:
            left_thrust=1600
        elif left_thrust<=1400:
            left_thrust=1400
        
        if right_thrust>=1600:
            right_thrust=1600
        elif right_thrust<=1400:
            right_thrust=1400

        T200_thruster.send_T200_PWM_Width([left_thrust,right_thrust])
        current_time = datetime.now()
        Servo.sync_Write_Angle([left_angle,right_angle])
        read_servo_angle_list = Servo.sync_Read_Angle()
        
        with open(csv_log_file,'a') as file:
            writer = csv.DictWriter(file, fieldnames=['Timestamp_log','left_angle','right_angle','left_thrust','right_thrust','read_left_angle','read_right_angle'])
            writer.writerow({'Timestamp_log':current_time,'left_angle':left_angle,'right_angle':right_angle,'left_thrust':left_thrust,'right_thrust':right_thrust,
            'read_left_angle':read_servo_angle_list[0],'read_right_angle':read_servo_angle_list[1]})
            print("Time and Data",current_time,left_angle,right_angle,left_thrust,right_thrust,read_servo_angle_list)

        file.close() 

if __name__ == '__main__':
    T200_Servo_command()


