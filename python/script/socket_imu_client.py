'''
Date: 2022-08-27 22:00:19
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-09-01 20:43:57
FilePath: \script\socket_imu_client.py
'''

# '''
# Date: 2022-08-27 16:18:18
# LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
# LastEditTime: 2022-08-27 16:20:20
# FilePath: \Underwater_Client\socket_imu_client.py
# '''


import csv

from Socket_IMU import IMUSocketClass 
# from datetime import datetime 

###################################################################
## Test the Socket_IMU Class, Client

## 1. initialize the UDP communication 
msgFromClient       = "Hello, UDP Server. This is Client from PC!".encode('utf-8')
serverAddressPort   = ("169.254.10.50", 54000)

IMUSocket_client = IMUSocketClass(serverAddressPort[0],serverAddressPort[1],0)

## 2. create a CSV file to store the IMU data
csv_file_name = IMUSocket_client.create_csv()

print("UDP Client Communication Begin!")

IMUSocket_client.UDPClientSocket.sendto(msgFromClient, serverAddressPort)
msgFromServer = IMUSocket_client.UDPClientSocket.recvfrom(1024)
print("Server IP Address:{}".format(msgFromServer[1]))


while True:
    IMUSocket_client.UDPClientSocket.sendto(msgFromClient, serverAddressPort)
    msgFromServer = IMUSocket_client.UDPClientSocket.recvfrom(1024)

    with open(csv_file_name, 'a', newline='') as file :

        print(format(msgFromServer[0].decode('gbk')))

        imu_data_decode = IMUSocket_client.decode_imu_data_to_list(msgFromServer[0].decode('gbk'))
        writer = csv.DictWriter(file, fieldnames=['Accel_x', 'Accel_y', 'Accel_z', 'Roll', 'Pitch', 'Yaw','Timestamp', ])
        writer.writerow({'Accel_x':imu_data_decode[0],'Accel_y':imu_data_decode[1],'Accel_z':imu_data_decode[2],'Roll':imu_data_decode[3],'Pitch':imu_data_decode[4],'Yaw':imu_data_decode[5],'Timestamp':imu_data_decode[6]})

    # UDPClientSocket.close()

    file.close()

###################################################################
