'''
Date: 2022-07-27 21:48:16
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-07-29 00:32:42
FilePath: /python/IMU_Microstrain.py
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
import time 
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

    def __init__(self, SampleRate: int) -> None:
        
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


    def configIMUChannel(self):

        self.ahrsIMUCh.append(mscl.MipChannel(mscl.MipTypes.CH_FIELD_SENSOR_SCALED_ACCEL_VEC, mscl.SampleRate.Hertz(self.SampleRate)))
        self.ahrsIMUCh.append(mscl.MipChannel(mscl.MipTypes.CH_FIELD_SENSOR_SCALED_GYRO_VEC, mscl.SampleRate.Hertz(self.SampleRate)))
        self.ahrsIMUCh.append(mscl.MipChannel(mscl.MipTypes.CH_FIELD_SENSOR_EULER_ANGLES, mscl.SampleRate.Hertz(self.SampleRate)))
        # self.ahrsIMUCh.append(mscl.MipChannel(mscl.MipTypes.CH_FIELD_SENSOR_TEMPERATURE_STATISTICS, mscl.SampleRate.Hertz(self.SampleRate)))

        # set the active channesl for the AHRS/IMU class on the Node
        self.node.setActiveChannelFields(mscl.MipTypes.CLASS_AHRS_IMU, self.ahrsIMUCh)
        self.node.enableDataStream(mscl.MipTypes.CLASS_AHRS_IMU)

        return 


    def parseDataStream_Number(self, Timeout_ms: int, PacketNumber):

        try:
            # get all the packets that have been collected, with a timeout of Timeout_ms miliseconds
            packets = self.node.getDataPackets(Timeout_ms, PacketNumber)

            for packet in packets:
                packet.descriptorSet()  # the descriptor set of the packet

                # get all of the points in the packet
                points = packet.data()

                for dataPoint in points:
                    print("Data Frame: %-20s" % dataPoint.channelName() + " |  %10s"  % dataPoint.as_string())

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
Microstrain = Microstrain_Class(SampleRate=100)
Microstrain.configIMUChannel()

# parse PacketNumber packet of the data stream
# Microstrain.parseDataStream_Number(200, 5)

# parse packets of the data stream to update the
# latest IMU data into Class properties
# Microstrain.parseDataStrean_Loop(200)

Microstrain.setToIdle()

################################################
