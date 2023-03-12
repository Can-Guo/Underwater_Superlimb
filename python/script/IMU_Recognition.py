'''
Date: 2023-02-14 16:52:34
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-10 21:31:45
FilePath: /script/IMU_Recognition.py
'''


import socket as Socket

## socket TCP : Ubuntu(server) <==> Raspberry Pi 4B
s= Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
s.bind(("10.12.234.126",54000))
s.listen(10)
client_socket,clienttAddr=s.accept()

## socket TCP : Ubuntu(client) <==> Mi-notebook (server)
import socket as Socket
socket_Mi = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
socket_Mi.settimeout(5000)
socket_Mi.connect(("10.13.228.137", 7788))

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
    # print("Name", file_name)
    
    with open(file_name, 'a') as file:
        writer = csv.writer(file, delimiter = ',', quotechar='"', quoting = csv.QUOTE_MINIMAL)
        writer.writerow(['Timestamp_cmd','imu_cmd'])
        #,'throat_mics_cmd')

    file.close()
    
    return file_name

## Encode IMU and Throat Microphone Message/ Token into string Message to be send
def encodeIMU_MI(Data_IMU, Data_Mi):
    send_string = str('')
    send_string = str(Data_IMU) + ',' + str(Data_Mi)

    print("Encoded Data: %s" % send_string)

    return send_string


def IMU_recognition(csv_imu_file, csv_command_file):
    #global Socket_Command
    global socket_Mi

    time.sleep(5)

    global roll_before 
    global pitch_before
    global yaw_before

    ## Setting label and initialize the current mode

    # 0: waiting mode
    # 1: lateral left; 2: lateral right; 3: flexion
    # 4: extension   ; 5: left rotation  6: right rotation
           
    IMU_Command_Label = ['0','1','2','3','4','5','6']
    current_mode = IMU_Command_Label[0]
    # last_mode = str('0')


    X_threshold = 20.0 #/180.0 * np.pi 
    Y_threshold = 20.0 #/180.0 * np.pi 
    Z_threshold = 20.0 #/180.0 * np.pi 

    # while(True):

    ## read csv file of IMU data 
    IMU_data_frame_one = readIMUCSV(csv_imu_file,1)
    
    Data_List_one = np.array(IMU_data_frame_one)

    last_frame_number.append(Data_List_one.shape[0])

    timestamp_frame_one = Data_List_one[:,0]

    #Client_Data = Socket_Command.UDPServerSocket.recvfrom(1024)
    print("Client Continue")

    try:
        Data_Mi = socket_Mi.recv(1024, 0x40)
    except BlockingIOError as e:
        print("Error!",e)


    if len(last_frame_number) == 1:

        if Data_List_one.shape[1] >= 4:
            roll_record_before = Data_List_one[0:last_frame_number[0],4]
            pitch_record_before = Data_List_one[0:last_frame_number[0],5]
            yaw_record_before = Data_List_one[0:last_frame_number[0],6]

            roll_before = np.mean(roll_record_before)
            pitch_before = np.mean(pitch_record_before)
            yaw_before = np.mean(yaw_record_before)

            print("Roll Before: %f, Pitch Before: %f, Yaw Before: %f" % (roll_before,pitch_before,yaw_before))


        for i in range(last_frame_number[0]):#len(timestamp_frame[0])):

            with open(csv_command_file, 'a') as file:
                writer = csv.DictWriter(file, fieldnames=['Timestamp_cmd','imu_cmd']) #,'Throat_Mi'])
                writer.writerow({'Timestamp_cmd':timestamp_frame_one[i],'imu_cmd':current_mode})
            
            file.close()
                    # last_frame_number.append(len(timestamp_frame))

        print("Last Frame Number",last_frame_number)

            # Socekt Message Sending
            # Send_string = encodeIMU_MI(current_mode, (Data_Mi.decode('utf-8')))
            # print("SEND STRING: %s" % Send_string)

        # Socekt Message Sending
        # Send_String = current_mode.encode('utf-8')
        Send_string = encodeIMU_MI(current_mode, (Data_Mi.decode('utf-8')))
        client_socket.send(Send_string.encode('utf-8'))

        print("send for Once!\r\n") 

        print("Please Wait until the IMU data is stable !\r\n")
        

    while(True):

        time.sleep(0.25)
        
        IMU_data_frame = readIMUCSV(csv_imu_file,1)

        Data_List = np.array(IMU_data_frame)

        last_frame_number.append(Data_List.shape[0])

        timestamp_frame = Data_List[:,0]

        #Client_Data = client_socket.UDPServerSocket.recvfrom(1024)
        
        # if(Client_Data[0].decode('utf-8')=='so'):
        #     print("So\r\n")
        #     print("Quit! ")
        #     sys.exit()

        try:
            Data_Mi = socket_Mi.recv(1024, 0x40)
        except BlockingIOError as e:
            print("Error!",e)
    

        if len(last_frame_number) >= 2 : 


            for i in range(last_frame_number[-2],last_frame_number[-1]):
                
                if Data_List.shape[1] >= 4:
                    roll_record_new = Data_List[last_frame_number[-2]:last_frame_number[-1],4]
                    pitch_record_new = Data_List[last_frame_number[-2]:last_frame_number[-1],5]
                    yaw_record_new = Data_List[last_frame_number[-2]:last_frame_number[-1],6]

                    # break
                
                if(((roll_record_new[i-last_frame_number[-2]] - roll_before) >= X_threshold) and (np.abs(pitch_record_new[i-last_frame_number[-2]] -pitch_before) <= Y_threshold)):
                    current_mode = IMU_Command_Label[3]
                    # break

                if((yaw_record_new[i-last_frame_number[-2]] - yaw_before) >= Z_threshold):
                    current_mode = IMU_Command_Label[6]
                    # break

                if((roll_record_new[i-last_frame_number[-2]] - roll_before) <= -X_threshold):
                    current_mode = IMU_Command_Label[4]
                    # break

                if((pitch_record_new[i-last_frame_number[-2]] - pitch_before) <= -Y_threshold):
                    current_mode = IMU_Command_Label[1]
                    # break

                if((yaw_record_new[i-last_frame_number[-2]] - yaw_before) <= -2*Z_threshold):
                    current_mode = IMU_Command_Label[5]
                    # break

                if((pitch_record_new[i-last_frame_number[-2]] - pitch_before) >= 1.5*Y_threshold):
                    current_mode = IMU_Command_Label[2]
                    # break

                if (( np.abs(yaw_record_new[i-last_frame_number[-2]] - yaw_before) <= np.abs(0.5*Z_threshold))
                    and (np.abs(pitch_record_new[i-last_frame_number[-2]] - pitch_before) <= np.abs(0.5*Y_threshold)) 
                    and (np.abs(roll_record_new[i-last_frame_number[-2]] - roll_before) <= np.abs(0.5*X_threshold))):
                    current_mode = IMU_Command_Label[0]
                    pass 
                    # break
                
                with open(csv_command_file, 'a') as file:
                    writer = csv.DictWriter(file, fieldnames=['Timestamp_cmd','imu_cmd']) #,'Throat_Mi'])
                    writer.writerow({'Timestamp_cmd':timestamp_frame[i],'imu_cmd':current_mode})
                
                file.close()                

            # Socekt Message Sending
            Send_string = encodeIMU_MI(current_mode, (Data_Mi.decode('utf-8')))
            # print("SEND STRING: %s" % Send_string)
            client_socket.send(Send_string.encode('utf-8'))
        
    

def plot_csv_cmd(csv_command_file):

    plt.figure(figsize=(20,10))

    ax1 = plt.subplot(2,1,1)
    


    data_frame = readIMUCSV(csv_command_file,2)
    data_frame.drop(['Timestamp_cmd'], axis=1,inplace=True)
    data_list = np.array(data_frame)

    frame_number = data_list.shape[0]

    time_sequence = np.linspace(0, frame_number/100, frame_number)

    ax2 = plt.subplot(2,1,2)

    plt.plot(time_sequence,data_list, label='command_class')

    plt.xticks(fontsize = 10)
    plt.yticks(fontsize = 10)

    plt.xlabel('Time(second)', fontsize = 15)
    ax2.legend(fontsize = 15)
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
    
    file_name = take_str_name(flag=1)
    print(file_name)
    command_file = createCommandCSV(file_name)
    IMU_recognition(csv_command_file=command_file, csv_imu_file=file_name)

    ## Test the results
    file_name = take_str_name(flag=2)
    print(file_name)
    plot_csv_cmd(file_name)
    


else:
    print("Errors! Please check your codes.\r\n")
    
