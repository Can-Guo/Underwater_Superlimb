'''
Date: 2023-03-13 16:18:42
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-13 22:19:24
FilePath: /script/Test_Servo.py
'''

import os 
import csv 
import time 
import pandas as pd 
from datetime import datetime
from Dynamixel import Servo_Class
import numpy as np 
import matplotlib.pyplot as plt 
import scienceplots
plt.style.use(['science','no-latex'])

Sample_Rate = 30
A = 90
T = 2 
f = 1/T 
omega = 2 * np.pi * (f)


def creatLogcsv(flag=1):
    cwd = os.path.abspath('.')
    time_mark = datetime.now()
    if flag == 1:
        file_name = str(cwd) + '/servo_thruster_data_0311/' + str(time_mark) + '_test_servo_sine.csv'
    elif flag == 2:
        file_name = str(cwd) + '/servo_thruster_data_0311/' + str(time_mark) + '_test_servo_step.csv'
    print("Path to log data:", file_name)

    with open(file_name,'a') as file:
        writer = csv.writer(file,delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['Timestamp_log','left_angle_cmd','right_angle_cmd','left_angle_rt','right_angle_rt'])

    file.close()

    return file_name 


def sin_function(A,omega,t):

    return A*np.sin(omega*t)


def time_extraction(time_seg):
    time_seg_str = str(time_seg)
    str_split = time_seg_str.split(':')
    second_realtime = float(str_split[0])*3600 + float(str_split[1])*60 + float(str_split[2])*1 + 1

    return second_realtime


def time_match(start_time_stamp,time_stamp):
    time_seg_str = str(time_stamp-start_time_stamp)
    str_split = time_seg_str.split(':')
    time_in_axis = float(str_split[0])*3600 + float(str_split[1])*60 + float(str_split[2])

    return time_in_axis


def time_sequence_method(time_stamp_column_dataframe):
    time_Sequences = []
    start_time_stamp = datetime.strptime(time_stamp_column_dataframe[0],'%Y-%m-%d %H:%M:%S:%f')

    for time_stamp in time_stamp_column_dataframe:
        time_stamp = datetime.strptime(time_stamp,'%Y-%m-%d %H:%M:%S:%f')
        time_Sequences.append(time_match(start_time_stamp,time_stamp))

    return time_Sequences


def test_servo_sine():

    PortName = '/dev/ttyUSB0'
    Servo = Servo_Class(PortName, 57600)
    Servo.enable_Torque()
    csv_file_name = creatLogcsv(flag=1)
    time_seq = np.linspace(0, 4, 400)
    
    for t in time_seq:
        angle_cmd = sin_function(A,omega,t)
        current_time = datetime.now()
        Servo.sync_Write_Angle([angle_cmd,angle_cmd])
        time.sleep(0.005)
        angle_realtime = Servo.sync_Read_Angle()
        
        with open(csv_file_name,'a') as file:
            writer = csv.DictWriter(file, fieldnames=['Timestamp_log','left_angle_cmd','right_angle_cmd',
                                                      'left_angle_rt','right_angle_rt'])
            writer.writerow({'Timestamp_log':current_time,'left_angle_cmd':angle_cmd,'right_angle_cmd':angle_cmd,
                             'left_angle_rt':angle_realtime[0],'right_angle_rt':angle_realtime[1]})

    Servo.disable_Torque()


def test_servo_step():
    
    PortName = '/dev/ttyUSB0'
    Servo = Servo_Class(PortName, 57600)
    Servo.enable_Torque()
    csv_file_name = creatLogcsv(flag=2)
    # time_seq = np.linspace(0, 4, 400)
    Servo.sync_Write_Angle([0,0])
    time.sleep(1)
    
    angle_cmd = [0,90,0,-90,0]
    
    for i in range(5):
        
        Servo.sync_Write_Angle([angle_cmd[i],angle_cmd[i]])

        for j in range(30):
            angle_realtime = Servo.sync_Read_Angle()    
            current_time = datetime.now()
            with open(csv_file_name,'a') as file:
                writer = csv.DictWriter(file, fieldnames=['Timestamp_log','left_angle_cmd','right_angle_cmd',
                                                        'left_angle_rt','right_angle_rt'])
                writer.writerow({'Timestamp_log':current_time,'left_angle_cmd':angle_cmd[i],'right_angle_cmd':angle_cmd[i],
                                'left_angle_rt':angle_realtime[0],'right_angle_rt':angle_realtime[1]})
            
            time.sleep(0.04)

    Servo.disable_Torque()


def plot_servo_animation(csv_file_name):
    cwd = os.path.abspath('.')
    csv_file_path = str(cwd) + '/servo_thruster_data_0311/' + csv_file_name
    servo_frame = pd.read_csv(csv_file_path)
    frame_number = len(servo_frame['Timestamp_log'])
    servo_frame.drop(['Timestamp_log'], axis=1, inplace=True)

    servo_frame_list = np.array(servo_frame)

    print("Frame Number:", frame_number)
    time_sequence = np.linspace(0, frame_number/Sample_Rate, frame_number)
    # Time_sequence_servo = time_sequence_method(servo_frame_list[:,0])

    left_angle_cmd = servo_frame_list[:,0]
    right_angle_cmd = servo_frame_list[:,1]
    left_angle_rt = servo_frame_list[:,2]
    right_angle_rt = servo_frame_list[:,3]

    plt.figure(figsize=[20,10])

    start_time = datetime.now()
    
    while(True):
        
        now_time = datetime.now()
        time_seg = now_time - start_time
        time = time_extraction(time_seg)
        # print("Time_seg:",time) 
        if((int)(time*Sample_Rate) > frame_number):
           break
           
        plt.clf()

        ax1 = plt.subplot(2,1,1)
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)], left_angle_cmd[0:(int)(time*Sample_Rate)], 'r-', label = 'left_angle_cmd')
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)], left_angle_rt[0:(int)(time*Sample_Rate)], 'g-.', label = 'left_angle_realtime')
        # plt.plot(time_sequence[0:(int)(time*Sample_Rate)], accel_z_record[0:(int)(time*Sample_Rate)], 'b-', label = 'acceleration_z')
        
        # ax1.set_title("Acceleration in x-y-z axis",fontsize=20)

        plt.ylim([-180, 180])
        plt.xlim(0,(int)(time+1))

        plt.xticks(fontsize = 15)
        plt.yticks(fontsize = 15)

        plt.ylabel('Angle of Servos (degree)', fontsize = 20)

        plt.legend(fontsize = 15)        

        ax2 = plt.subplot(2,1,2)
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)],  right_angle_cmd[0:(int)(time*Sample_Rate)], 'r-', label = 'right_angle_realtime')
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)], right_angle_rt[0:(int)(time*Sample_Rate)], 'g-.', label = 'right_angle_realtime')
        # plt.plot(time_sequence[0:(int)(time*Sample_Rate)],   yaw_record[0:(int)(time*Sample_Rate)], 'b-', label = 'yaw angle')
        
        # ax2.set_title("Euler Angle in x-y-z axis",fontsize=20)

        plt.ylim([-180, 180])
        plt.xlim(0,(int)(time+1))

        plt.xticks(fontsize = 15)
        plt.yticks(fontsize = 15)

        plt.ylabel('Angle of Servos (degree)', fontsize = 20)
        plt.xlabel("Time(second)")
        
        plt.legend(fontsize = 15)

        plt.pause(0.2)

    # pass 


def plot_servo_static(csv_file_name):
    
    csv_name = csv_file_name
    cwd = os.path.abspath('.')
    csv_file_path = str(cwd) + '/servo_thruster_data_0311/' + csv_file_name
    servo_frame = pd.read_csv(csv_file_path)
    frame_number = len(servo_frame['Timestamp_log'])
    servo_frame.drop(['Timestamp_log'], axis=1, inplace=True)

    servo_frame_list = np.array(servo_frame)

    print("Frame Number:", frame_number)
    time_sequence = np.linspace(0, frame_number/Sample_Rate, frame_number)
    # Time_sequence_servo = time_sequence_method(servo_frame_list[:,0])

    left_angle_cmd = servo_frame_list[:,0]
    right_angle_cmd = servo_frame_list[:,1]
    left_angle_rt = servo_frame_list[:,2]
    right_angle_rt = servo_frame_list[:,3]

    plt.figure(figsize=(20,10))

    ax1 = plt.subplot(2,1,1)
    plt.plot(time_sequence, left_angle_cmd, 'r-', label = 'left_angle_command')
    plt.plot(time_sequence, left_angle_rt, 'g-.', label = 'left_angle_realtime')
    # plt.plot(time_sequence[0:(int)(time*Sample_Rate)], accel_z_record[0:(int)(time*Sample_Rate)], 'b-', label = 'acceleration_z')

    plt.ylim([-110, 110])
    plt.xlim(0,time_sequence[-1])

    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)

    plt.ylabel('Angle of Servos (degree)', fontsize = 20)

    plt.legend(fontsize = 15)        

    ax2 = plt.subplot(2,1,2)
    plt.plot(time_sequence,  right_angle_cmd, 'r-', label = 'right_angle_command')
    plt.plot(time_sequence, right_angle_rt, 'g-.', label = 'right_angle_realtime')
    # plt.plot(time_sequence[0:(int)(time*Sample_Rate)],   yaw_record[0:(int)(time*Sample_Rate)], 'b-', label = 'yaw angle')
    
    # ax2.set_title("Euler Angle in x-y-z axis",fontsize=20)

    plt.ylim([-110, 110])
    plt.xlim(0,time_sequence[-1])

    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)

    plt.ylabel('Angle of Servos (degree)', fontsize = 20)
    plt.xlabel("Time(second)",fontsize=20)
    
    plt.legend(fontsize = 15)

    # current = datetime.now()
    cwd = os.path.abspath('.')
    fig_name = str(cwd) + '/image_servo_thrust/' + str(csv_name) + '.png'
    plt.savefig(fig_name,dpi=600)

    plt.show()

     
if __name__ == '__main__':
    # Method 1.1: test servo with Sine Function Command
    # test_servo_sine()

    # Method 1.2: test servo with Step Function Command
    # test_servo_step()

    # Method 2: Plot the servo angle figure
    # plot_servo_animation('2023-03-13 21:32:00.939927_test_servo.csv')

    plot_servo_static('2023-03-13 22:17:57.945619_test_servo_sine.csv')

    

