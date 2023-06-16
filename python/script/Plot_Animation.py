'''
Date: 2023-03-10 15:05:18
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-05-22 12:21:16
FilePath: /script/Plot_Animation.py
'''

import numpy as np 
import matplotlib.pyplot as plt 
import scienceplots
plt.style.use(['science','no-latex'])
import pandas as pd 
import os 
from datetime import datetime 


Sample_Rate = 100
Accel_limit = 30
Angle_limit = 180


def time_extraction(time_seg):
    time_seg_str = str(time_seg)
    str_split = time_seg_str.split(':')
    second_realtime = float(str_split[0])*3600 + float(str_split[1])*60 + float(str_split[2])*1 + 1
    # print(str_split)
    return second_realtime


def time_match(start_time_stamp,time_stamp):
    # print("Time Ser:", start_time_stamp,time_stamp)
    time_seg_str = str(time_stamp-start_time_stamp)
    str_split = time_seg_str.split(':')
    # print("str_Plit:",str_split)
    time_in_axis = float(str_split[0])*3600 + float(str_split[1])*60 + float(str_split[2])

    return time_in_axis


def time_sequence_method(time_stamp_column_dataframe):
    time_Sequences = []
    start_time_stamp = datetime.strptime(time_stamp_column_dataframe[0],'%Y-%m-%d %H:%M:%S:%f')

    for time_stamp in time_stamp_column_dataframe:
        time_stamp = datetime.strptime(time_stamp,'%Y-%m-%d %H:%M:%S:%f')
        time_Sequences.append(time_match(start_time_stamp,time_stamp))

    return time_Sequences


def Plot_animation(csv_file_name):
    cwd = os.path.abspath('.') 
    # csv_file_name_2 = csv_file_name
    csv_file_path = str(cwd) + '/csv_imu_0310/' + csv_file_name
    data_frame = pd.read_csv(csv_file_path)
    print("Read CSV File Path:", csv_file_path)

    frame_number = len(data_frame['Acceleration_x'])
    print("Frame Number:", frame_number)
    time_sequence = np.linspace(0, frame_number/Sample_Rate, frame_number)

    data_frame.drop(['Timestamp'], axis=1, inplace=True)



    csv_command_file = str(cwd) + '/csv_command_0310/' + csv_file_name
    Command_time_frame = pd.read_csv(csv_command_file)
    cmd_frame_number = len(Command_time_frame['imu_cmd'])
    Command_time_list = np.array(Command_time_frame)
    Command_value = Command_time_list[:,1]
    time_sequence_2 = time_sequence_method(Command_time_list[:,0])
   
    # delete specific column of data in Dataframe, such as timestamp column

    Time_sequence_2 = np.linspace(0,cmd_frame_number/Sample_Rate,cmd_frame_number)


    data_list = np.array(data_frame)

    accel_x_record = data_list[:,0]
    accel_y_record = data_list[:,1]
    accel_z_record = data_list[:,2]
    
    roll_record = data_list[:,3]
    pitch_record = data_list[:,4]
    yaw_record = data_list[:,5]

    plt.figure(figsize=[18,10])

    start_time = datetime.now()  

    # for i in range((int)((frame_number-1)/Sample_Rate*Refresh_rate)):
    
    while(True):
        
        now_time = datetime.now()
        time_seg = now_time - start_time
        time = time_extraction(time_seg)
        # print("Time_seg:",time) 
        if((int)(time*Sample_Rate) > 40*Sample_Rate):
            cwd = os.path.abspath('.')
            fig_name = str(cwd) + '/image_imu/' + str(csv_file_name) + '_animation.png'
            plt.savefig(fig_name,dpi=600)
            plt.pause(10)
            break
           
        plt.clf()

        ax1 = plt.subplot(3,1,1)
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)], accel_x_record[0:(int)(time*Sample_Rate)], 'r--', label = 'acceleration_x')
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)], accel_y_record[0:(int)(time*Sample_Rate)], 'g-.', label = 'acceleration_y')
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)], accel_z_record[0:(int)(time*Sample_Rate)], 'b-', label = 'acceleration_z')
        
        # ax1.set_title("Acceleration in x-y-z axis",fontsize=15)

        plt.ylim([-Accel_limit, Accel_limit])
        plt.xlim(0,(int)(time+0.5))

        plt.xticks(fontsize = 15)
        plt.yticks(fontsize = 15)

        plt.ylabel('Acceleration(m/s^2)', fontsize = 15)

        plt.legend(loc='upper left',fontsize = 15)        

        ax2 = plt.subplot(3,1,2)
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)],  roll_record[0:(int)(time*Sample_Rate)], 'r--', label = 'roll angle')
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)], pitch_record[0:(int)(time*Sample_Rate)], 'g-.', label = 'pitch angle')
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)],   yaw_record[0:(int)(time*Sample_Rate)], 'b-', label = 'yaw angle')
        
        # ax2.set_title("Euler Angle in x-y-z axis",fontsize=15)

        plt.ylim([-Angle_limit, Angle_limit])
        plt.xlim(0,(int)(time+0.5))

        plt.xticks(fontsize = 15)
        plt.yticks(fontsize = 15)

        plt.ylabel('Euler Angle(degree)', fontsize = 15)
        # plt.xlabel("Time(second)",fontsize=15)
        
        plt.legend(loc='upper left',fontsize = 15)

        ax3 = plt.subplot(3,1,3)
        plt.plot(Time_sequence_2[0:(int)(time*Sample_Rate)],  Command_value[0:(int)(time*Sample_Rate)], 'c-', label = 'command_index')
        # plt.title("Command Index after Head Motion Classification",fontsize=15)
        # plt.xlim(Time_sequence_2[0],Time_sequence_2[-1])
        plt.ylim(-1,8)
        plt.xlim(0,(int)(time+0.5))
        plt.xticks(fontsize = 15)
        plt.yticks(fontsize = 15)
        plt.ylabel("Command Index", fontsize=15)
        plt.xlabel('Time(second)', fontsize = 15)
        plt.legend(loc='upper left',fontsize=15)


        plt.pause(0.01)



def Plot_static(csv_file):
    cwd = os.path.abspath('.')
    CSV_file_name = csv_file
    # csv_file = str(cwd) + '/csv_imu_0310/' + csv_file
    csv_file = str(cwd) + '/csv_record_imu/' + csv_file
    data_frame = pd.read_csv(csv_file)
    IMU_value = np.array(data_frame)

    time_sequence_1 = time_sequence_method(IMU_value[:,0])

    frame_number = len(data_frame['Acceleration_x'])
    print("frame number:", frame_number)

    # csv_command_file = str(cwd) + '/csv_command_0310/' + CSV_file_name
    # Command_time_frame = pd.read_csv(csv_command_file)
    # cmd_frame_number = len(Command_time_frame['imu_cmd'])
    # Command_time_list = np.array(Command_time_frame)
    # Command_value = Command_time_list[:,1]
    # time_sequence_2 = time_sequence_method(Command_time_list[:,0])
   
    time_sequence = np.linspace(0, frame_number/Sample_Rate, frame_number)
    # delete specific column of data in Dataframe, such as timestamp column

    # Time_sequence_2 = np.linspace(0,cmd_frame_number/Sample_Rate,cmd_frame_number)

    # data_frame.drop(['Timestamp'], axis = 1, inplace = True)  

    data_list = np.array(data_frame)

    if data_frame.shape[1] <= 3:
        print("Euler Angle Plot")
        roll_record = data_list[:,1]
        pitch_record = data_list[:,2]
        yaw_record = data_list[:,3]
        
        plt.figure(figsize=[20,10])

        plt.plot(time_sequence_1, roll_record, 'r--', label = 'roll angle')
        plt.plot(time_sequence_1, pitch_record, 'g-.', label = 'pitch angle')
        plt.plot(time_sequence_1, yaw_record, 'b-', label = 'yaw angle')
        plt.ylim([-np.pi, np.pi])
        plt.xlim(time_sequence_1[0],time_sequence_1[frame_number-1])

        plt.xticks(fontsize = 10)
        plt.yticks(fontsize = 10)

        plt.ylabel('Angle (degree)', fontsize = 15)
        plt.xlabel('Timestamp', fontsize = 15)

        plt.legend(fontsize = 15)
        plt.grid()


    elif data_frame.shape[1] > 3:
        print("Acceleration and Euler Angle Plot")
        accel_x_record = data_list[:,1] * 9.8
        accel_y_record = data_list[:,2] * 9.8
        accel_z_record = data_list[:,3] * 9.8

        roll_record = data_list[:,4]*180/np.pi
        pitch_record = data_list[:,5]*180/np.pi
        yaw_record = data_list[:,6]*180/np.pi

        # with plt.style.context(['science','no-latex']):
        plt.figure(figsize=(10,10))

        ax1 = plt.subplot(2,1,1)

        plt.plot(time_sequence, accel_x_record, 'r--', label = 'acceleration_x')
        plt.plot(time_sequence, accel_y_record, 'g-.', label = 'acceleration_y')
        plt.plot(time_sequence, accel_z_record, 'b-', label = 'acceleration_z')
        
        # ax1.set_title("Acceleration along x-y-z axis",fontsize=15)

        plt.ylim([-20, 20])
        # plt.xlim(time_sequence[0],time_sequence[-1])
        # plt.xlim(25,65)
        plt.xlim(0,40)

        plt.xticks(fontsize = 20)
        plt.yticks(fontsize = 20)

        plt.ylabel('Acceleration(m/s^2)', fontsize = 20)
        # plt.xlabel('Time(second)', fontsize = 15)

        # plt.legend(fontsize = 15)
        plt.legend(loc='upper left',fontsize=20)
        # plt.grid()

        ax2 = plt.subplot(2,1,2)

        # ax3 = ax2.twinx()

        plt.plot(time_sequence, roll_record, 'r--', label = 'roll angle')
        plt.plot(time_sequence, pitch_record, 'g-.', label = 'pitch angle')
        plt.plot(time_sequence, yaw_record, 'b-', label = 'yaw angle')

        # ax2.set_title("Euler Angles along x-y-z axis",fontsize=15)
        plt.ylim([-180, 180])
        # plt.xlim(time_sequence[0],time_sequence[-1])
        # plt.xlim(25,65)
        plt.xlim(0,40)
        plt.xticks(fontsize = 20)
        plt.yticks(fontsize = 20)
        plt.ylabel('Angle(degree)', fontsize = 20)
        ax2.legend(loc='upper left',fontsize = 20)
        # plt.grid()

        # plt.figure(figsize=[20,10])

        # ax3 = plt.subplot(3,1,3)
        # plt.plot(Time_sequence_2, Command_value, 'c-', label = 'command_index')
        # # plt.title("Command Index after Head Motion Classification",fontsize=15)
        # # plt.xlim(Time_sequence_2[0],Time_sequence_2[-1])
        # plt.ylim(-1,8)
        # plt.xlim(0,40)
        # plt.xticks(fontsize = 20)
        # plt.yticks(fontsize = 20)
        # plt.ylabel("Command Index", fontsize=20)
        # plt.xlabel('Time(second)', fontsize = 20)
        # plt.legend(loc='upper left',fontsize=15)


    cwd = os.path.abspath('.')
    # fig_name = str(cwd) + '/image_imu/' + str(CSV_file_name) + '_imu_cmd.png'
    fig_name = str(cwd) + '/image_imu/' + str(CSV_file_name) + '_imu_no_cmd.png'
    plt.savefig(fig_name,dpi=600)

    plt.show()

    # return fig_name



## Method 1: plot the imu raw data in realtime animation
# csv_file_name = '2023-03-11 22:46:47:80_imu_data_exp_1_OK.csv'
# csv_file_name = '2023-03-11 22:46:47:80_imu_data_exp_1_OK copy.csv'

#### For IMU Data Demonstration
# csv_file_name = 'Extension-Fri Jan 13 09:43:50 2023_imu_data.csv'
csv_file_name = 'Left_Bending-Fri Jan 13 09:30:50 2023_imu_data.csv'
# Plot_animation(csv_file_name)

## Method 2: plot the imu raw data and command in static
Plot_static(csv_file_name)






