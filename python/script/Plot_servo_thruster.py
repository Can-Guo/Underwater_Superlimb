'''
Date: 2023-03-12 22:27:05
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-13 15:01:27
FilePath: /script/Plot_servo_thruster.py
'''


import numpy as np 
import matplotlib.pyplot as plt 
import scienceplots 
plt.style.use(['science','no-latex'])
import pandas as pd 
import os 
from datetime import datetime



def time_match(start_time_stamp,time_stamp):
    # print("Time Ser:", start_time_stamp,time_stamp)
    time_seg_str = str(time_stamp-start_time_stamp)
    str_split = time_seg_str.split(':')
    # print("str_Plit:",str_split)
    time_in_axis = float(str_split[0])*3600 + float(str_split[1])*60 + float(str_split[2])

    return time_in_axis


def time_sequence(time_stamp_column_dataframe):
    time_Sequences = []
    start_time_stamp = datetime.strptime(time_stamp_column_dataframe[0],'%Y-%m-%d %H:%M:%S.%f')

    for time_stamp in time_stamp_column_dataframe:
        time_stamp = datetime.strptime(time_stamp,'%Y-%m-%d %H:%M:%S.%f')
        time_Sequences.append(time_match(start_time_stamp,time_stamp))

    return time_Sequences


def plot_servo_thrust_static(csv_file):
    cwd = os.path.abspath('.')
    csv_file_name = csv_file
    csv_file = str(cwd) + '/servo_thruster_data_0311/' + csv_file 
    data_frame = pd.read_csv(csv_file)

    servo_thrust_value = np.array(data_frame)

    frame_number = len(servo_thrust_value[:,1])

    print("frame number:",frame_number)

    Time_Sequences = time_sequence(servo_thrust_value[:,0])
    # print("Time_Sequence:",Time_Sequences)

    ## control command send to servo and thruster
    left_servo_cmd   = servo_thrust_value[:,1]
    right_servo_cmd  = servo_thrust_value[:,2]
    left_thrust_cmd  = servo_thrust_value[:,3]
    right_thrust_cmd = servo_thrust_value[:,4]
    # servo angles feedback to raspberryp Pi
    # TODO: However, no thruster force feedback
    left_servo_read  = servo_thrust_value[:,5]
    right_servo_read = servo_thrust_value[:,6]

    plt.figure(figsize=[20,10])
    # print("Time sequence:",Time_Sequences[0:10])

    plt.subplot(3,1,1)

    plt.plot(Time_Sequences, left_servo_cmd, 'r-', label = 'Control Command of Left Servo ')
    plt.plot(Time_Sequences, left_servo_read, 'g-.', label = 'Feedback Angle of Left Servo')
    plt.title("Control Command and Angle Feedback of Left Servo",fontsize=15)

    plt.xlim(Time_Sequences[0],Time_Sequences[-1])
    plt.ylim([-130,130])
    plt.ylabel("Servo Angle (degree)",fontsize=15)
    # plt.xlabel("Time (second)",fontsize=15)
    plt.legend(fontsize=15)
    
    plt.subplot(3,1,2)
    plt.plot(Time_Sequences, right_servo_cmd, 'b-', label = 'Control Command of Right Servo ')
    plt.plot(Time_Sequences, right_servo_read, 'c-.', label = 'Feedback Angle of Right Servo')
    
    plt.title("Control Command and Angle Feedback of Right Servo",fontsize=15)

    plt.xlim(Time_Sequences[0],Time_Sequences[-1])
    plt.ylim([-130,130])
    plt.ylabel("Servo Angle (degree)",fontsize=15)
    # plt.xlabel("Time (second)",fontsize=15)
    plt.legend(fontsize=15)

    # plt.figure(figsize=[20,10])

    plt.subplot(3,1,3)
    plt.plot(Time_Sequences, left_thrust_cmd, 'y-', label = 'PWM Command of Left Thruster')
    plt.plot(Time_Sequences, right_thrust_cmd, 'k-.', label = 'PWM Command of Right Thruster')
    plt.title("Control Command and Angle Feedback of Thrusters",fontsize=15)

    
    plt.ylim([1350,1650])
    plt.ylabel("PWM Value of Thrusters",fontsize=15)
    plt.xlabel("Time (second)",fontsize=15)
    plt.legend(fontsize=15)

    plt.xlim(Time_Sequences[0],Time_Sequences[-1])

    cwd = os.path.abspath('.')
    fig_name = str(cwd) + '/image_servo_thrust/' + str(csv_file_name) + '.png'
    plt.savefig(fig_name,dpi=600)

    plt.show()
    


if __name__ == '__main__':
    csv_name = '2023-03-11 22:47:12.135232_exp_1_OK_1.csv'
    plot_servo_thrust_static(csv_name)


