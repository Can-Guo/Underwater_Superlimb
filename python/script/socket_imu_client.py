'''
Date: 2022-08-27 22:00:19
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-09-01 21:50:48
FilePath: \script\socket_imu_client.py
'''

# '''
# Date: 2022-08-27 16:18:18
# LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
# LastEditTime: 2022-08-27 16:20:20
# FilePath: \Underwater_Client\socket_imu_client.py
# '''


from Socket_IMU import IMUSocketClass 

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


## 3. record imu data into a CSV file
IMUSocket_client.record_csv_data(csv_file_name)

## 4. plot the imu data from a CSV file created before by record_csv_file() Method
# IMUSocket_client.plot_csv_data('imu_data_2022-09-01 21-44-18_save.csv')

###################################################################
