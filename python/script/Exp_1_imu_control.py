'''
Date: 2023-03-10 20:10:13
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-11 23:05:15
FilePath: /script/Exp_1_imu_control.py
'''

import socket as Socket

## socket TCP: ubuntu(server) <==> Raspberry Pi 4B
port = 3300
## socket TCP : Ubuntu(server) <==> Raspberry Pi 4B
s= Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
s.bind(("10.12.234.126",port))
s.listen(10)
client_socket,clienttAddr=s.accept()

## import libs
import time
import numpy as np 
import os 
import csv 
import pandas as pd 
import sys 
from datetime import datetime 
import matplotlib.pyplot as plt 
import scienceplots 
plt.style.use(['science','no-latex'])

## List to label the frame number
last_frame_number =[]

roll_before = 0.0
pitch_before = 0.0
yaw_before = 0.0

## Method 1: read CSV file

def readIMUCSV(csv_file, flag):
    cwd = os.path.abspath('.')
    # CSV_file_name = csv_file

    if flag == 1:
        csv_file = str(cwd) + '/csv_imu_0310/' + csv_file
    elif flag == 2:
        csv_file = str(cwd) + '/csv_command_0310/' + csv_file

    data_frame = pd.read_csv(csv_file)

    if flag == 1:
        frame_number = len(data_frame['Timestamp'])
    elif flag == 2:
        frame_number = len(data_frame['Timestamp_cmd'])

    # global last_frame_number
    # last_frame_number.append(frame_number)

    print("Frame Number: %d \r\n" % frame_number)

    return data_frame

def createCommandCSV(file_name):
    cwd = os.path.abspath('.')
    # time_mark = datetime.now()
    file_name = str(cwd) + '/csv_command_0310/' + file_name # + str(time_mark) + '.csv'
    print("Name to be creat:", file_name)
    
    with open(file_name, 'a') as file:
        writer = csv.writer(file, delimiter = ',', quotechar='"', quoting = csv.QUOTE_MINIMAL)
        writer.writerow(['Timestamp_cmd','imu_cmd','roll_delta','pitch_delta','yaw_delta'])

    file.close()
    
    return file_name


## Encode IMU Message/ Token into string Message to be send
def encodeIMU_control(next_state,current_roll,current_pitch, current_yaw):
    # send_string = str('')
    current_roll = round(current_roll,2)
    current_pitch = round(current_pitch,2)
    current_yaw = round(current_yaw,2)
    send_string = str(next_state) + ',' + str(current_roll) +',' + str(current_pitch) + ',' + str(current_yaw) + '!'

    print("Encoded Data: %s " % send_string)

    return send_string


def IMU_control(csv_imu_file, csv_command_file):

    ## calibration of the IMU sensor
    print("Please Wait until the IMU data is stable for 5 seconeds!\r\n")
        
    time.sleep(5)

    global roll_before
    global pitch_before
    global yaw_before

    IMU_command_label = ['0','1','2','3','4','5','6']
    next_mode = IMU_command_label[0]

    X_threshold = 20.0 #/180.0 * np.pi 
    Y_threshold = 20.0 #/180.0 * np.pi 
    Z_threshold = 20.0 #/180.0 * np.pi 

    ## read csv file for calibration
    IMU_data_frame_one = readIMUCSV(csv_imu_file, 1)
    Data_list_one = np.array(IMU_data_frame_one)

    last_frame_number.append(Data_list_one.shape[0])

    timestamp_frame_one = Data_list_one[:,0]

    print("Client continue...")

    # try:
    
    ## Calibration:
    if len(last_frame_number) == 1:

        if Data_list_one.shape[1]>=4:
            roll_record_before = Data_list_one[0:last_frame_number[0],4]
            pitch_record_before = Data_list_one[0:last_frame_number[0],5]
            yaw_record_before = Data_list_one[0:last_frame_number[0],6]

            roll_before = np.mean(roll_record_before)
            pitch_before = np.mean(pitch_record_before)
            yaw_before = np.mean(yaw_record_before)
        
            print("Calibration Results: roll %f, \tpitch %f, \tyaw %f" %  (roll_before,pitch_before,yaw_before))

        for i in range(last_frame_number[0]):
    
            with open(csv_command_file, 'a') as file:
                writer = csv.DictWriter(file, fieldnames=['Timestamp_cmd','imu_cmd','roll_delta','pitch_delta','yaw_delta']) #,'Throat_Mi'])
                writer.writerow({'Timestamp_cmd':timestamp_frame_one[i],'imu_cmd':next_mode, 
                                 'roll_delta':roll_record_before[i],
                                 'pitch_delta':pitch_record_before[i],'yaw_delta':yaw_record_before[i]})
            
            file.close()

        print("Last Frame Number: %d", last_frame_number)

        # Socekt Message Sending
        Send_string = encodeIMU_control(next_mode, roll_before, pitch_before, yaw_before)
        client_socket.send(Send_string.encode('utf-8'))

        print("send for Once!\r\n") 

        print("Calibration is Done! Please begin control!\r\n")


    while(True):
        time.sleep(0.001)
        IMU_data_frame = readIMUCSV(csv_imu_file,1)

        Data_list = np.array(IMU_data_frame)

        last_frame_number.append(Data_list.shape[0])

        timestamp_frame = Data_list[:,0]

        if len(last_frame_number) >= 2:

            for i in range(last_frame_number[-2],last_frame_number[-1]):

                if Data_list.shape[1] >= 4:
                    roll_record_new = Data_list[last_frame_number[-2]:last_frame_number[-1],4]
                    pitch_record_new = Data_list[last_frame_number[-2]:last_frame_number[-1],5]
                    yaw_record_new = Data_list[last_frame_number[-2]:last_frame_number[-1],6]

                if(((roll_record_new[i-last_frame_number[-2]] - roll_before) >= X_threshold)): 
                    # and (np.abs(pitch_record_new[i-last_frame_number[-2]] -pitch_before) <= Y_threshold)):
                    next_mode = IMU_command_label[3]
                
                if((yaw_record_new[i-last_frame_number[-2]] - yaw_before) >= Z_threshold):
                    next_mode = IMU_command_label[6]
                    # break

                if((roll_record_new[i-last_frame_number[-2]] - roll_before) <= -X_threshold):
                    next_mode = IMU_command_label[4]
                    # break

                if((pitch_record_new[i-last_frame_number[-2]] - pitch_before) <= -Y_threshold):
                    next_mode = IMU_command_label[1]
                    # break

                if((yaw_record_new[i-last_frame_number[-2]] - yaw_before) <= -Z_threshold):
                    next_mode = IMU_command_label[5]
                    # break

                if((pitch_record_new[i-last_frame_number[-2]] - pitch_before) >= Y_threshold):
                    next_mode = IMU_command_label[2]
                    # break

                if (( np.abs(yaw_record_new[i-last_frame_number[-2]] - yaw_before) <= np.abs(0.5*Z_threshold))
                    and (np.abs(pitch_record_new[i-last_frame_number[-2]] - pitch_before) <= np.abs(0.5*Y_threshold)) 
                    and (np.abs(roll_record_new[i-last_frame_number[-2]] - roll_before) <= np.abs(0.5*X_threshold))):
                    next_mode = IMU_command_label[0]
                    pass 

                with open(csv_command_file, 'a') as file:
                    writer = csv.DictWriter(file, fieldnames=['Timestamp_cmd','imu_cmd','roll_delta','pitch_delta','yaw_delta'])
                    writer.writerow({'Timestamp_cmd':timestamp_frame[i],'imu_cmd':next_mode,'roll_delta':roll_record_new[i-last_frame_number[-2]],
                                     'pitch_delta':pitch_record_new[i-last_frame_number[-2]],'yaw_delta':yaw_record_new[i-last_frame_number[-2]]})
                
                file.close()  
            
                Send_string = encodeIMU_control(next_mode,
                                                (roll_record_new[i-last_frame_number[-2]] - roll_before),
                                                (pitch_record_new[i-last_frame_number[-2]] - pitch_before),
                                                (yaw_record_new[i-last_frame_number[-2]]- yaw_before))
                
                client_socket.send(Send_string.encode('utf-8'))


def plot_csv_cmd(csv_command_file):
    
    plt.figure(figsize=(20,10))

    data_frame = readIMUCSV(csv_command_file,2)
    data_frame.drop(['Timestamp_cmd'], axis=1,inplace=True)
    
    data_list = np.array(data_frame)
    frame_number = data_list.shape[0]

    time_sequence = np.linspace(0, frame_number/100, frame_number)
    
    ax1 = plt.subplot(2,1,1)
    plt.plot(time_sequence,data_list[:,0], 'c-', label='command_index')
    ax1.legend(fontsize = 20)
    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)

    ax2 = plt.subplot(2,1,2)
    plt.plot(time_sequence,data_list[:,1], 'r-',  label='roll')
    plt.plot(time_sequence,data_list[:,2], 'g-.', label='pitch')
    plt.plot(time_sequence,data_list[:,3], 'b--', label='yaw')

    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)

    plt.xlabel('Time(second)', fontsize = 20)
    ax2.legend(fontsize = 20)
    plt.grid()
    plt.show()


def take_str_name(flag):
    if flag == 1:
        path = os.path.abspath('.') + str('/csv_imu_0310/')
    elif flag == 2:
        path = os.path.abspath('.') + str('/csv_command_0310/')
        
    list = os.listdir(path=path)
    list.sort()

    return list[-1]


if __name__ == '__main__':
    
    record_or_plot = 2

    ## Record and transmitte
    if record_or_plot==1:
        file_name = take_str_name(flag=1)
        print(file_name)
        command_file = createCommandCSV(file_name)
        IMU_control(csv_command_file=command_file, csv_imu_file=file_name)
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
    # ## Test the results
    elif record_or_plot==2:
        file_name = take_str_name(flag=2)
        print(file_name)
        plot_csv_cmd(file_name)
    


else:
    print("Errors! Please check your codes.\r\n")

