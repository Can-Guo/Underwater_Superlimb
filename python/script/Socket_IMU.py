'''
Date: 2022-09-01 16:54:03
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-09-01 21:48:11
FilePath: \script\Socket_IMU.py
'''

import socket
import platform

from datetime import datetime 
import os 
import csv 

import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt  


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

        self.serverAddressPort = (local_ip, local_port)
        self.msgFromClient = "Hello, UDP Server. This is Client from PC!".encode('utf-8')
        
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


    ## Encode imu data, from list into a string with comma symbol

    def encode_imu_data_to_str(self, number_list):
        
        send_string = str('')
        for data in number_list:
            send_string = send_string + str(data) + ','

        print("Send Data: %s" % send_string)

        return send_string


    ## imu data as string, convert into number list

    def decode_imu_data_to_list(self, recv_string_gtk):

        imu_data_decode = recv_string_gtk.split(',')
        
        return imu_data_decode


    ## create a CSV file to save the IMU data

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


    ## record IMU data into a CSV file create by creat_csv() method
    def record_csv_data(self, csv_file_name):        
        
        while True:

            self.UDPClientSocket.sendto(self.msgFromClient, self.serverAddressPort)
            msgFromServer = self.UDPClientSocket.recvfrom(1024)

            with open(csv_file_name, 'a', newline='') as file :

                print(format(msgFromServer[0].decode('gbk')))

                imu_data_decode = self.decode_imu_data_to_list(msgFromServer[0].decode('gbk'))
                writer = csv.DictWriter(file, fieldnames=['Accel_x', 'Accel_y', 'Accel_z', 'Roll', 'Pitch', 'Yaw','Timestamp', ])
                writer.writerow({'Accel_x':imu_data_decode[0],'Accel_y':imu_data_decode[1],'Accel_z':imu_data_decode[2],'Roll':imu_data_decode[3],'Pitch':imu_data_decode[4],'Yaw':imu_data_decode[5],'Timestamp':imu_data_decode[6]})

            # UDPClientSocket.close()

            file.close()


    ## Plot the data for a CSV file recorded by
    def plot_csv_data(self, csv_file_name, imu_sample_rate=100):

        cwd = os.path.abspath('.')
        cwd = os.path.dirname(cwd)

        if sys_platform == 'windows':
            csv_file = str(cwd) + '\csv\\' + csv_file_name 
        elif sys_platform == 'linux':
            csv_file = str(cwd) + '/csv/' + csv_file_name 

        data_frame = pd.read_csv(csv_file)

        frame_number = len(data_frame['Accel_x'])
        print("Frame Number inside CSV file: %d" % frame_number)
        time_sequence = np.linspace(0, frame_number/imu_sample_rate,frame_number)

        # data_frame.drop(['TimeStamp'], axis = 1, inplace= True)

        data_list = np.array(data_frame)
        
        accel_x_record = data_list[:,0]
        accel_y_record = data_list[:,1]
        accel_z_record = data_list[:,2]

        roll_record = data_list[:,3]
        pitch_record = data_list[:,4]
        yaw_record = data_list[:,5]

        plt.figure(figsize=(20,10))

        ax1 = plt.subplot(2,1,1)

        plt.plot(time_sequence, accel_x_record, 'r--', label = 'acceleration_x')
        plt.plot(time_sequence, accel_y_record, 'g-.', label = 'acceleration_y')
        plt.plot(time_sequence, accel_z_record, 'b-', label = 'acceleration_z')
        
        ax1.set_title("Acceleration in x-y-z axis", fontsize = 20)

        plt.ylim([-2, 2])
        plt.xlim(time_sequence[0],time_sequence[frame_number-1])

        plt.xticks(fontsize = 10)
        plt.yticks(fontsize = 10)

        plt.ylabel('Acceleration(g)', fontsize = 15)
        # plt.xlabel('Time(second)', fontsize = 15)

        plt.legend(fontsize = 15)
        plt.grid()

        ax2 = plt.subplot(2,1,2)

        plt.plot(time_sequence, roll_record, 'r--', label = 'roll angle')
        plt.plot(time_sequence, pitch_record, 'g-.', label = 'pitch angle')
        plt.plot(time_sequence, yaw_record, 'b-', label = 'yaw angle')

        ax2.set_title("Euler Angles", fontsize = 20)

        plt.ylim([-np.pi, np.pi])
        plt.xlim(time_sequence[0],time_sequence[frame_number-1])

        plt.xticks(fontsize = 10)
        plt.yticks(fontsize = 10)

        plt.ylabel('Angle (radian)', fontsize = 15)
        plt.xlabel('Time(second)', fontsize = 15)

        plt.legend(fontsize = 15)
        plt.grid()
        
        current_time = datetime.now()
        current_time = current_time.strftime("%Y-%m-%d %H-%M-%S")

        cwd = os.path.abspath('.')
        cwd = os.path.dirname(cwd)

        if sys_platform == 'windows':
            fig_name = str(cwd) + '\\figure\\' + str(current_time) + '.png' 
        elif sys_platform == 'linux':
            fig_name = str(cwd) + '/figure/' + str(current_time) + '.png'

        plt.savefig(fig_name,dpi=600)

        plt.show()

        return fig_name


########################################################################
## Class Testing Begins!
# socket_imu = IMUSocketClass()

# csv_file_name = socket_imu.create_csv()
# socket_imu.record_csv_data(csv_file_name)

# socket_imu.plot_csv_data('imu_data_2022-09-01 21-44-18_save.csv')

## END
########################################################################
