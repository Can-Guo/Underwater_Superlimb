'''
Date: 2022-09-01 16:54:03
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-09-01 20:18:31
FilePath: \script\Socket_IMU.py
'''

from http import server
import socket

from datetime import datetime 
import os 
import csv 
import platform


## Differ the system platform for different file path system
if platform.system().lower() == 'windows':
    print("当前的操作系统是windows")
    sys_platform = 'windows'
elif platform.system().lower() == 'linux':
    print("当前的操作系统是linux")
    sys_platform = 'linux'

# print(sys_platform)


class IMUSocketClass(object):

    def __init__(self, local_ip="169.254.10.50", local_port=54000, server_or = 1):

        try:
            self.UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            if server_or == 1:
                self.UDPServerSocket.bind((local_ip, local_port))
                print("Socket Server Initialization is Successfyl!\r\n")
            elif server_or == 0:
                print("Socket Client Initialization is Successfyl!\r\n")

        except:
            print("UDP Initialization Failed! Please check your ip and port!\r\n")


    ## Get the data and send to other computer.
    
    def sendback_imu_data(self):

        # 3. formate the imu data

        # 4. send back to PC or Ubuntu

        return


    ## 

    def encode_imu_data_to_str(self, number_list):
        send_string = str('')
        for data in number_list:
            send_string = send_string + str(data) + ','

        print("Send Data: %s" % send_string)

        return send_string


    ## imu data as string, convert into number list

    def decode_imu_data_to_list(self, recv_string_gtk):

        # print(recv_string)
        imu_data_decode = recv_string_gtk.split(',')
        
        return imu_data_decode


    def create_csv(self):
        cwd = os.path.abspath('.')
        cwd = os.path.dirname(cwd)

        time_mark = datetime.now()

        time_mark = time_mark.strftime("%Y-%m-%d %H-%M-%S")
        if sys_platform == 'windows':
            file_name = str(cwd) + '\csv\imu_data_' + str(time_mark) + '_save.csv'
        elif sys_platform == 'linux':
            file_name = str(cwd) + '/csv/imu_data_' + str(time_mark) + '_save.csv'

        # print(file_name)

        with open(file_name, 'a', newline='') as file:
            writer = csv.writer(file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
            writer.writerow(['Accel_x', 'Accel_y', 'Accel_z', 'Roll', 'Pitch', 'Yaw', 'Timestamp', ])

        file.close()

        return file_name


