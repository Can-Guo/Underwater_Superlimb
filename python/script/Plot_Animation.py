'''
Date: 2023-03-10 15:05:18
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-13 00:13:50
FilePath: /script/Plot_Animation.py
'''

import numpy as np 
import matplotlib.pyplot as plt 
import scienceplots
# plt.style.use(['science','no-latex'])
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
    print(str_split)
    return second_realtime


def Plot_animation(csv_file_name):
    cwd = os.path.abspath('.') 
    csv_file_name_2 = csv_file_name
    csv_file_path = str(cwd) + '/csv_imu_0310/' + csv_file_name
    data_frame = pd.read_csv(csv_file_path)

    frame_number = len(data_frame['Acceleration_x'])
    print("Frame Number:", frame_number)
    time_sequence = np.linspace(0, frame_number/Sample_Rate, frame_number)

    data_frame.drop(['Timestamp'], axis=1, inplace=True)

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
        if((int)(time*Sample_Rate) > frame_number):
           break
           
        plt.clf()

        ax1 = plt.subplot(2,1,1)
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)], accel_x_record[0:(int)(time*Sample_Rate)], 'r--', label = 'acceleration_x')
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)], accel_y_record[0:(int)(time*Sample_Rate)], 'g-.', label = 'acceleration_y')
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)], accel_z_record[0:(int)(time*Sample_Rate)], 'b-', label = 'acceleration_z')
        
        ax1.set_title("Acceleration in x-y-z axis",fontsize=20)

        plt.ylim([-Accel_limit, Accel_limit])
        plt.xlim(0,(int)(time+1))

        plt.xticks(fontsize = 15)
        plt.yticks(fontsize = 15)

        plt.ylabel('Acceleration(m/s^2)', fontsize = 20)

        plt.legend(fontsize = 15)        

        ax2 = plt.subplot(2,1,2)
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)],  roll_record[0:(int)(time*Sample_Rate)], 'r--', label = 'roll angle')
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)], pitch_record[0:(int)(time*Sample_Rate)], 'g-.', label = 'pitch angle')
        plt.plot(time_sequence[0:(int)(time*Sample_Rate)],   yaw_record[0:(int)(time*Sample_Rate)], 'b-', label = 'yaw angle')
        
        ax2.set_title("Euler Angle in x-y-z axis",fontsize=20)

        plt.ylim([-Angle_limit, Angle_limit])
        plt.xlim(0,(int)(time+1))

        plt.xticks(fontsize = 15)
        plt.yticks(fontsize = 15)

        plt.ylabel('Angle(degree)', fontsize = 20)
        plt.xlabel("Time(second)")
        
        plt.legend(fontsize = 15)

        plt.pause(0.01)

    
    # return



def Plot_static(csv_file):
    cwd = os.path.abspath('.')
    CSV_file_name = csv_file
    csv_file = str(cwd) + '/csv_imu_0310/' + csv_file
    data_frame = pd.read_csv(csv_file)

    csv_command_file = str(cwd) + '/csv_command_0310/' + CSV_file_name
    Command_frame = pd.read_csv(csv_command_file)

    Command_value = (np.array(Command_frame))[:,1]

    frame_number = len(data_frame['Acceleration_x'])
    print("frame number:", frame_number)
    time_sequence = np.linspace(0, frame_number/Sample_Rate, frame_number)

    # delete specific column of data in Dataframe, such as timestamp column
    data_frame.drop(['Timestamp'], axis = 1, inplace = True)  


    # print("Column Number", data_frame.shape[1])

    data_list = np.array(data_frame)

    if data_frame.shape[1] <= 3:
        print("Euler Angle Plot")
        roll_record = data_list[:,0]
        pitch_record = data_list[:,1]
        yaw_record = data_list[:,2]
        
        plt.figure(figsize=[20,10])

        plt.plot(time_sequence, roll_record, 'r--', label = 'roll angle')
        plt.plot(time_sequence, pitch_record, 'g-.', label = 'pitch angle')
        plt.plot(time_sequence, yaw_record, 'b-', label = 'yaw angle')
        plt.ylim([-np.pi, np.pi])
        plt.xlim(time_sequence[0],time_sequence[frame_number-1])

        plt.xticks(fontsize = 10)
        plt.yticks(fontsize = 10)

        plt.ylabel('Angle (degree)', fontsize = 15)
        plt.xlabel('Timestamp', fontsize = 15)

        plt.legend(fontsize = 15)
        plt.grid()


    elif data_frame.shape[1] > 3:
        print("Acceleration and Euler Angle Plot")
        accel_x_record = data_list[:,0]
        accel_y_record = data_list[:,1]
        accel_z_record = data_list[:,2]

        roll_record = data_list[:,3]
        pitch_record = data_list[:,4]
        yaw_record = data_list[:,5]

        # with plt.style.context(['science','no-latex']):
        plt.figure(figsize=(20,10))

        ax1 = plt.subplot(3,1,1)

        plt.plot(time_sequence, accel_x_record, 'r--', label = 'acceleration_x')
        plt.plot(time_sequence, accel_y_record, 'g-.', label = 'acceleration_y')
        plt.plot(time_sequence, accel_z_record, 'b-', label = 'acceleration_z')
        
        ax1.set_title("Acceleration in x-y-z axis",fontsize=20)

        plt.ylim([-30, 30])
        plt.xlim(time_sequence[0],time_sequence[frame_number-1])

        plt.xticks(fontsize = 10)
        plt.yticks(fontsize = 10)

        plt.ylabel('Acceleration(m/s^2)', fontsize = 15)
        # plt.xlabel('Time(second)', fontsize = 15)

        plt.legend(fontsize = 15)
        # plt.grid()

        ax2 = plt.subplot(3,1,2)

        # ax3 = ax2.twinx()

        plt.plot(time_sequence, roll_record, 'r--', label = 'roll angle')
        plt.plot(time_sequence, pitch_record, 'g-.', label = 'pitch angle')
        plt.plot(time_sequence, yaw_record, 'b-', label = 'yaw angle')

        # ax3.plot(time_sequence, Command_value, 'c-.', label = 'command_index')
        
        # fmt = '%1d'
        # yticks=mtick.FormatStrFormatter(fmt)
        # ax2.yaxis.set_major_formatter(yticks)
        # ax3.set_ylim(0,6)

        ax2.set_title("Euler Angles",fontsize=20)

        plt.ylim([-180, 180])
        plt.xlim(time_sequence[0],time_sequence[frame_number-1])

        plt.xticks(fontsize = 10)
        plt.yticks(fontsize = 10)

        plt.ylabel('Angle(degree)', fontsize = 15)
        

        ax2.legend(fontsize = 15)
        # plt.grid()

        ax3 = plt.subplot(3,1,3)
        plt.plot(time_sequence, Command_value, 'c-', label = 'command_index')
        ax3.set_title("command index",fontsize=20)
        plt.xlim(time_sequence[0],time_sequence[frame_number-1])
        plt.ylabel("Command Index", fontsize=15)
        plt.xlabel('Time(second)', fontsize = 15)
        plt.legend(fontsize=15)

    # current = datetime.now()
    cwd = os.path.abspath('.')
    fig_name = str(cwd) + '/image_imu/' + str(CSV_file_name) + '.png'
    plt.savefig(fig_name,dpi=600)

    plt.show()

    return fig_name



## Method 1: plot the imu raw data in realtime animation
csv_file_name = '2023-03-11 21:09:18:31_imu_data.csv'
# Plot_animation(csv_file_name)

## Method 2: plot the imu raw data and command in static
# csv_file_name = ''
Plot_static(csv_file_name)






