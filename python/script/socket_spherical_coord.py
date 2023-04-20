'''
Date: 2023-04-17 14:18:21
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-04-20 14:50:44
FilePath: /script/socket_spherical_coord.py
'''


import socket as Socket
import time 
import os 
import pandas as pd 
import numpy as np 


### Server ###
## socket TCP: ubuntu(server) <==> Raspberry Pi 4B
port = 8888
## socket TCP : Ubuntu(server) <==> Raspberry Pi 4B
s= Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
s.bind(("10.24.24.199",port))
s.listen(10)
client_socket,clienttAddr=s.accept()


## Method 1: read CSV file
def readIMUCSV(csv_file, flag):
    cwd = os.path.abspath('.')
    # CSV_file_name = csv_file

    if flag == 1:
        csv_file = str(cwd) + '/csv_imu_0417/' + csv_file
    elif flag == 2:
        # csv_file = str(cwd) + '/csv_command_0310/' + csv_file
        pass 

    data_frame = pd.read_csv(csv_file)

    if flag == 1:
        frame_number = len(data_frame['Timestamp'])
    elif flag == 2:
        # frame_number = len(data_frame['Timestamp_cmd'])
        pass  

    # global last_frame_number
    # last_frame_number.append(frame_number)

    print("Frame Number: %d \r\n" % frame_number)

    return data_frame


def take_str_name(flag):
    if flag == 1:
        path = os.path.abspath('.') + str('/csv_imu_0417/')
    elif flag == 2:
        # path = os.path.abspath('.') + str('/csv_command_0310/')
        pass 
        
    list = os.listdir(path=path)
    list.sort()

    return list[-1]


def encode_imu_data(data_list):
    
    string_send = str(data_list[0]) + ',' + str(data_list[1]) + ',' + str(data_list[2]) + ',' + str(data_list[3]) + ',' + str(data_list[4]) + ',' + str(data_list[5]) + '!'
    print("Sent to Raspberry Pi:",string_send)
    return string_send


if __name__ == '__main__':
    
    ## Take file name of the CSV file 
    csv_imu_file = take_str_name(flag=1)

    while(True):

        ## read csv file for calibration
        IMU_data_frame_one = readIMUCSV(csv_imu_file, 1)
        Data_list_one = np.array(IMU_data_frame_one)

        # print(Data_list_one.shape[1])

        time.sleep(0.1) 
        Data_list = []
        for i in range(1,7):
            sum = 0 
            for j in range(1,5):
                sum = sum + Data_list_one[-j][i]
            temp_float = np.round((sum + Data_list_one[-1][i])/5,3)
            Data_list.append(temp_float)

        send_string = encode_imu_data(Data_list)

        # print("Data_List:", Data_list)

        client_socket.send(send_string.encode('utf-8'))





