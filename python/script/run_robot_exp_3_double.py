'''
Date: 2023-03-14 15:06:39
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-15 22:11:02
FilePath: /script/run_robot_exp_3_double.py
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
port = 3377
socket_pi = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
socket_pi.settimeout(5000)
socket_pi.connect(("10.12.234.126",port))
# socket_pi.connect(("192.168.43.201",port))


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


def decodeIMUandMI(Data_Server):
    
    imu_and_voice = Data_Server.split('!')

    imu_and_voice_list = imu_and_voice[0].split('#')
    imu_cmd_list = imu_and_voice_list[0].split(',')
    print("Data_to_Decode", imu_and_voice_list[0])

    if(len(imu_and_voice_list) < 2):
        print("-----------------------------------------------")
        return [[' 0','0'],['Q','Q']]
    else:
        # len(imu_and_voice_list[0]) == 2:
        voice_list = imu_and_voice_list[1].split(',')
        return imu_cmd_list, voice_list 


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
    index = 0

    flag = 0
    last_flag = flag 
    #0:voice
    #1:head
    voice_head_flag=0
    csv_log_file = creatLogcsv()

    while(i<=1000):

        msgFromServer = socket_pi.recv(1024)
        Decoded_imu_list, Decoded_voice_list = decodeIMUandMI(msgFromServer.decode('utf-8'))
        temp_index = index 
        if(len(Decoded_voice_list)<2):
            flag = 0

        else:
            if(len(Decoded_voice_list)<2):
                flag = 0
            else:
                print("From Server:",Decoded_voice_list)
                
            if Decoded_voice_list[0]=='do' and Decoded_voice_list[1] =='S':
                flag = 2
                print("Voice is do S!")
                
            elif Decoded_voice_list[0]=='do' and Decoded_voice_list[1] =='L':
                flag = 1
                print("Voice is do L!")
            elif Decoded_voice_list[0]=='re' and Decoded_voice_list[1] =='S':
                flag = 6
                print("Voice is re S!")
            elif Decoded_voice_list[0]=='re' and Decoded_voice_list[1] =='L':
                flag = 5
                print("Voice is re L!")
            elif Decoded_voice_list[0]=='fa' and Decoded_voice_list[1] =='S':
                flag = 3
                print("Voice is me S!")
            elif Decoded_voice_list[0]=='fa' and Decoded_voice_list[1] =='L':
                flag = 4
                print("Voice is me L!")

            elif Decoded_voice_list[0]=='so':#and Decoded_voice_list[1] =='S':
                flag = 7
                if(voice_head_flag==1):
                    voice_head_flag=0
                else:
                    voice_head_flag=1
                print("Voice is fa !")
            elif Decoded_voice_list[0]=='me':#and Decoded_voice_list[1] =='L':
                flag = 8
                print("Voice is so !")
            
            if Decoded_voice_list[1] != 'Q' and voice_head_flag==0:
                    index += 1
                    print("Index ", index)

            if(index!=temp_index):
                print("Temp and Index",index,temp_index)
                ## set thrust based on flag{}
                left_angle = -90
                right_angle = -90

                if   (flag==2 and last_flag == 2) or (flag==2 and i==0) or (last_flag != flag and flag==2):
                    left_thrust =  left_thrust + 30
                    # print("Speed Up Left")

                elif (flag==1 and last_flag == 1 ) or  (flag==2 and i==0) or (last_flag != flag and flag==1):
                    left_thrust = left_thrust - 30
                    # print("Speed Down Left")

                elif (flag==6 and last_flag == 6 ) or  (flag==2 and i==0) or (last_flag != flag and flag==6): 
                    right_thrust = right_thrust + 30

                elif (flag==5 and last_flag == 5 ) or  (flag==2 and i==0) or (last_flag != flag and flag==5): 
                    right_thrust = right_thrust - 30

                elif (flag==3 and last_flag == 3 ) or  (flag==2 and i==0) or (last_flag != flag and flag==3): 
                    left_thrust = left_thrust + 30
                    right_thrust = left_thrust

                elif (flag==4 and last_flag == 4 ) or  (flag==2 and i==0) or (last_flag != flag and flag==4): 
                    left_thrust = left_thrust - 30
                    right_thrust = left_thrust
                elif flag==8:
                    left_angle = 0
                    right_angle = 0
                    left_thrust = 1500
                    right_thrust = 1500

                # pass 
            if voice_head_flag == 1:
                print("Voice_head_flag",voice_head_flag)
                left_thrust = 1500
                right_thrust = 1500
                print("Decoded IMU Flag", Decoded_imu_list[0])
                
                if(Decoded_imu_list[0]=='0'):
                    left_angle = 0
                    right_angle = 0

                if(Decoded_imu_list[0]=='5'):
                    left_angle = left_angle - 90

                if(Decoded_imu_list[0]=='6'):
                    left_angle = left_angle + 90

                if(Decoded_imu_list[0]=='3'):
                    left_angle = left_angle - 90
                    right_angle = left_angle

                if(Decoded_imu_list[0]=='4'):
                    left_angle = left_angle + 90
                    right_angle = left_angle

                if(Decoded_imu_list[0]=='2'):
                    right_angle = right_angle + 90

                if(Decoded_imu_list[0]=='1'):
                    right_angle = right_angle - 90
                

        if flag == 0:
            left_angle =0
            right_angle=0
            left_thrust=1500
            right_thrust=1500
            print("Reset to Home Position!\r\n")

        ## send command to servo and thruster
        
        if left_thrust>=1590:
            left_thrust=1590
        elif left_thrust<=1410:
            left_thrust=1410
        
        if right_thrust>=1590:
            right_thrust=1590
        elif right_thrust<=1410:
            right_thrust=1410

        ## check and abjust the servo angles
        if left_angle>= 90:left_angle=90
        if left_angle<=-90:left_angle=-90
        if right_angle>= 90:right_angle=90
        if right_angle<=-90:right_angle=-90
        

        T200_thruster.send_T200_PWM_Width([left_thrust,right_thrust])
        current_time = datetime.now()
        Servo.sync_Write_Angle([left_angle,right_angle])
        read_servo_angle_list = Servo.sync_Read_Angle()
        
        with open(csv_log_file,'a') as file:
            writer = csv.DictWriter(file, fieldnames=['Timestamp_log','left_angle','right_angle','left_thrust','right_thrust','read_left_angle','read_right_angle'])
            writer.writerow({'Timestamp_log':current_time,'left_angle':left_angle,'right_angle':right_angle,'left_thrust':left_thrust,'right_thrust':right_thrust,
            'read_left_angle':read_servo_angle_list[0],'read_right_angle':read_servo_angle_list[1]})
            print("Time and Data",current_time,left_angle,right_angle,left_thrust,right_thrust,read_servo_angle_list)
        # file.close() 
        # time.sleep(2)
        last_flag = flag
        # last_flag = flag 
        i = i + 1

if __name__ == '__main__':
    T200_Servo_command()


