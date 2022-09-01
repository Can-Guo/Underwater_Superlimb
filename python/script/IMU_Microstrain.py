'''
Date: 2022-07-27 21:48:16
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-09-01 21:16:28
FilePath: \script\IMU_Microstrain.py
'''

#  How to run this demo file successfully after you've installed the python3-mscl package.
#  following the steps in https://github.com/LORD-MicroStrain/MSCL/blob/master/HowToUseMSCL.md?
#
#  1)Find the usb device name of the sensor: 
#     For Linux, it may be "/dev/ttyUSB0" or "/dev/ttyACM0" or similar.
#     For windows, it may be "COM3" or "COM4" or similar.
#     You may need help by command:  lsusb and ls /dev/ttyU* or ls /dev/ttyA*
#  2)Change the access permission of the usb device to accessable for the current user of the system, such as
#     Terminal #  sudo chmod 666 /dev/ttyACM0 
#  3)Run the source file directly, such as:
#     Terminal # python3 ./python_mscl_demo_simple.py


###### Here begins!  ######
import numpy as np 
import os 
import time
from datetime import datetime 
import csv 
import pandas as pd 
import matplotlib.pyplot as plt  
# import the mscl library

import sys

sys.path.append("/usr/share/python3-mscl/")
import mscl


#TODO: change these constants to match your setup
# COM_PORT = "COM4"
# Before your run this file, please change the access permission of the device, such as 
# sudo chmod 666 /dev/ttyACM0
COM_PORT = '/dev/ttyACM0'


class Microstrain_Class(object):

    def __init__(self, SampleRate: int = 100) -> None:
        
        try:
            # create Connection with specified USB port and Baud
            self.connection = mscl.Connection.Serial(COM_PORT)
            # create Node for the Connection created before
            self.node = mscl.InertialNode(self.connection)
            # ping the Node
            self.SUCCESS = self.node.ping()
            print("Ping IMU Node Success?", self.SUCCESS)
            
            if self.SUCCESS == True:
                    print("--------------------------------")
                    print("Connected! Device Information-->\r")
                    print("Model Name: %s \r" % self.node.modelName())
                    print("Model Number: %s \r" % self.node.modelNumber())
                    print("Serial Number: %s \r" % self.node.serialNumber())
                    print("Firmware Version: %s \r" % str(self.node.firmwareVersion()))
                    print("Initialization is done! \r")
                    print("--------------------------------\r\n")

            self.ahrsIMUCh = mscl.MipChannels()

            # SampleRate of the IMU, range from (int)(1,2,3,...,500)
            self.SampleRate = SampleRate

            # initialize the Data List for Acceleration and Gyroscope values in 3 axis
            self.LEN = (int)(0.1 * self.SampleRate)
            self.Accel_Microstrain = np.zeros([self.LEN,3])
            self.Gyro_Microstrain = np.zeros([self.LEN,3])
            self.Euler_Microstrain = np.zeros([self.LEN,3])


        except mscl.Error as e:
            print("MSCL Error Message:", e)


    def setToIdle(self):
        return self.node.setToIdle()


    def resumeDataStream(self):
        self.node.resume()


    def configIMUChannel(self, accel=False, gyro = False,  euler= True):

        if accel == True:
            self.ahrsIMUCh.append(mscl.MipChannel(mscl.MipTypes.CH_FIELD_SENSOR_SCALED_ACCEL_VEC, mscl.SampleRate.Hertz(self.SampleRate)))
        if gyro == True:
            self.ahrsIMUCh.append(mscl.MipChannel(mscl.MipTypes.CH_FIELD_SENSOR_SCALED_GYRO_VEC, mscl.SampleRate.Hertz(self.SampleRate)))
        if euler == True:
            self.ahrsIMUCh.append(mscl.MipChannel(mscl.MipTypes.CH_FIELD_SENSOR_EULER_ANGLES, mscl.SampleRate.Hertz(self.SampleRate)))
        
        # self.ahrsIMUCh.append(mscl.MipChannel(mscl.MipTypes.CH_FIELD_SENSOR_TEMPERATURE_STATISTICS, mscl.SampleRate.Hertz(self.SampleRate)))

        # set the active channesl for the AHRS/IMU class on the Node
        self.node.setActiveChannelFields(mscl.MipTypes.CLASS_AHRS_IMU, self.ahrsIMUCh)
        self.node.enableDataStream(mscl.MipTypes.CLASS_AHRS_IMU)

        return 

    def createCSV(self, accel = False, euler = True):
        cwd = os.path.abspath('.')
        time_mark = datetime.now()        
        file_name = str(cwd) + '/csv/data_' + str(time_mark) + '.csv'

        with open( file_name , 'a') as file:
            writer = csv.writer(file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
            # writer.writerow(['time', 'accel_x', 'accel_y', 'acce_z', 'roll', 'pitch', 'yaw'])
            if accel == True and euler == True:
                writer.writerow(['Timestamp', 'Accel_x', 'Accel_y', 'Accel_z', 'Roll', 'Pitch', 'Yaw'])
            elif accel == True and euler == False:
                writer.writerow(['Timestamp', 'Accel_x', 'Accel_y', 'Accel_z'])
            elif accel == False and euler == True:
                writer.writerow(['Timestamp', 'Roll', 'Pitch', 'Yaw'])

        file.close()
        
        print(file_name)
        
        return file_name


    def recordDataToCSV(self,accel = False, euler = True):

        # Create a CSV file first to record the data
        csv_file = self.createCSV(accel,euler)

        while self.SUCCESS:

            current_time = datetime.now()
            packets = self.node.getDataPackets(500, 1)

            for packet in packets:
                packet.descriptorSet()
                points = packet.data()

                for dataPoint in points:
                    if dataPoint.channelName() == 'scaledAccelX':
                        accel_x = dataPoint.as_float()
                    if dataPoint.channelName() == 'scaledAccelY':
                        accel_y = dataPoint.as_float()
                    if dataPoint.channelName() == 'scaledAccelZ':
                        accel_z = dataPoint.as_float()
                    if dataPoint.channelName() == 'roll':
                        roll = dataPoint.as_float()
                    if dataPoint.channelName() == 'pitch':
                        pitch = dataPoint.as_float()
                    if dataPoint.channelName() == 'yaw':
                        yaw = dataPoint.as_float()
                
            with open( csv_file, 'a') as file:
                # writer = csv.DictWriter(file, fieldnames=['time','accel_x','accel_y','accel_z','roll','pitch','yaw'])
                if accel == False and euler == True:
                    writer = csv.DictWriter(file, fieldnames=['Timestamp','Roll','Pitch','Yaw'])          
                    writer.writerow({'Timestamp':current_time,'Roll':roll,'Pitch':pitch,'Yaw':yaw})

                elif accel == True and euler == True:
                    writer = csv.DictWriter(file, fieldnames=['Timestamp', 'Accel_x', 'Accel_y', 'Accel_z', 'Roll', 'Pitch', 'Yaw'])
                    writer.writerow({'Timestamp':current_time,'Accel_x':accel_x,'Accel_y':accel_y,'Accel_z':accel_z,'Roll':roll,'Pitch':pitch,'Yaw':yaw})  

            file.close()
        # return csv_file


    def plotDataCSV(self, csv_file):
        cwd = os.path.abspath('.')
        csv_file = str(cwd) + '/csv/' + csv_file
        data_frame = pd.read_csv(csv_file)

        frame_number = len(data_frame['Timestamp'])
        print("frame number:", frame_number)
        time_sequence = np.linspace(0, frame_number/self.SampleRate, frame_number)

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

            plt.ylabel('Angle (radian)', fontsize = 15)
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

            plt.figure(figsize=(20,10))

            ax1 = plt.subplot(2,1,1)

            plt.plot(time_sequence, accel_x_record, 'r--', label = 'acceleration_x')
            plt.plot(time_sequence, accel_y_record, 'g-.', label = 'acceleration_y')
            plt.plot(time_sequence, accel_z_record, 'b-', label = 'acceleration_z')
            
            ax1.set_title("Acceleration in x-y-z axis")

            plt.ylim([-2, 2])
            plt.xlim(time_sequence[0],time_sequence[frame_number-1])

            plt.xticks(fontsize = 10)
            plt.yticks(fontsize = 10)

            plt.ylabel('Acceleration(g)', fontsize = 15)
            plt.xlabel('Time(second)', fontsize = 15)

            plt.legend(fontsize = 15)
            plt.grid()

            ax2 = plt.subplot(2,1,2)

            plt.plot(time_sequence, roll_record, 'r--', label = 'roll angle')
            plt.plot(time_sequence, pitch_record, 'g-.', label = 'pitch angle')
            plt.plot(time_sequence, yaw_record, 'b-', label = 'yaw angle')

            ax2.set_title("Euler Angles")

            plt.ylim([-np.pi, np.pi])
            plt.xlim(time_sequence[0],time_sequence[frame_number-1])

            plt.xticks(fontsize = 10)
            plt.yticks(fontsize = 10)

            plt.ylabel('Angle (radian)', fontsize = 15)
            plt.xlabel('Time(second)', fontsize = 15)

            plt.legend(fontsize = 15)
            plt.grid()

        current = datetime.now()
        cwd = os.path.abspath('.')
        fig_name = str(cwd) + '/figure/' + str(current) + '.png'
        plt.savefig(fig_name,dpi=600)

        plt.show()

        return fig_name


    def parseDataStream_Number(self, Timeout_ms: int, PacketNumber, accel_enable=False, euler_enable = True):

        try:
            # get all the packets that have been collected, with a timeout of Timeout_ms miliseconds
            packets = self.node.getDataPackets(Timeout_ms, PacketNumber)

            if accel_enable == False and euler_enable == True:

                for packet in packets:
                    packet.descriptorSet()  # the descriptor set of the packet

                    # get all of the points in the packet
                    points = packet.data()

                    for dataPoint in points:
                        if dataPoint.channelName() == 'roll':
                            roll = dataPoint.as_float()
                        if dataPoint.channelName() == 'pitch':
                            pitch = dataPoint.as_float()
                        if dataPoint.channelName() == 'yaw':
                            yaw = dataPoint.as_float()

                print("euler:", roll,pitch,yaw)
                return [roll,pitch,yaw]

            elif accel_enable == True and euler_enable == True:
                
                for packet in packets:
                    packet.descriptorSet()  # the descriptor set of the packet

                    # get all of the points in the packet
                    points = packet.data()

                    for dataPoint in points:

                        if dataPoint.channelName() == 'scaledAccelX':
                            accel_x = dataPoint.as_float()
                        if dataPoint.channelName() == 'scaledAccelY':
                            accel_y = dataPoint.as_float()
                        if dataPoint.channelName() == 'scaledAccelZ':
                            accel_z = dataPoint.as_float()
                    
                        if dataPoint.channelName() == 'roll':
                            roll = dataPoint.as_float()
                        if dataPoint.channelName() == 'pitch':
                            pitch = dataPoint.as_float()
                        if dataPoint.channelName() == 'yaw':
                            yaw = dataPoint.as_float()

                # print("Accel and Euler:", accel_x,accel_y,accel_z,roll,pitch,yaw)
                return [accel_x,accel_y,accel_z,roll,pitch,yaw]
                
                    # print("Data Frame: %-20s" % dataPoint.channelName() + " |  %10s"  % dataPoint.as_string())

        except mscl.Error as e:
            print("MSCL Error Message: ", e)


    def parseDataStrean_Loop(self, Timeout_ms: int):
        
        while True:
            packets = self.node.getDataPackets(Timeout_ms, self.SampleRate)

            for packet in packets:
                packet.descriptorSet()  # the descriptor set of the packet

                # get all of the points in the packet
                points = packet.data()

                for dataPoint in points:
                    if dataPoint.channelName() == 'roll':
                        roll = dataPoint.as_float()
                    if dataPoint.channelName() == 'pitch':
                        pitch = dataPoint.as_float()
                    if dataPoint.channelName() == 'yaw':
                        yaw = dataPoint.as_float()
                    if dataPoint.channelName() == 'scaledAccelX':
                        accel_x = dataPoint.as_float()
                    if dataPoint.channelName() == 'scaledAccelY':
                        accel_y = dataPoint.as_float()
                    if dataPoint.channelName() == 'scaledAccelZ':
                        accel_z = dataPoint.as_float()
                    if dataPoint.channelName() == 'scaledGyroX':
                        gyro_x = dataPoint.as_float()
                    if dataPoint.channelName() == 'scaledGyroY':
                        gyro_y = dataPoint.as_float()
                    if dataPoint.channelName() == 'scaledGyroZ':
                        gyro_z = dataPoint.as_float()

                
                AccelXYZ = np.array([accel_x, accel_y, accel_z])
                GyroXYZ = np.array([gyro_x, gyro_y, gyro_z])
                EulerXYZ = np.array([roll, pitch, yaw])

                self.Accel_Microstrain = np.roll(self.Accel_Microstrain, -3)
                self.Gyro_Microstrain = np.roll(self.Gyro_Microstrain, -3)
                self.Euler_Microstrain = np.roll(self.Euler_Microstrain, -3)

                self.Accel_Microstrain[self.LEN-1,:] = AccelXYZ
                self.Gyro_Microstrain[self.LEN-1,: ] = GyroXYZ
                self.Euler_Microstrain[self.LEN-1,:] = EulerXYZ
    
                print(self.Accel_Microstrain)

        # return


################################################
# Microstrain = Microstrain_Class(SampleRate=100)
# accel_enable = True; euler_enable = True
# Microstrain.configIMUChannel(accel_enable,0,euler_enable)

# 1. parse PacketNumber packet of the data stream
# Microstrain.parseDataStream_Number(200, 1, accel_enable, accel_enable)

# 2. Record data into CSV file
# Microstrain.recordDataToCSV(0,1)

# 3. plot data into Figure, and save into a PNG image
# Microstrain.plotDataCSV('data_2022-08-13 15:15:25.822028.csv')

# 4. parse packets of the data stream to update the
# latest IMU data into Class properties
# Microstrain.parseDataStrean_Loop(200)

# Microstrain.setToIdle()

################################################
