'''
Date: 2022-10-19 15:22:45
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-10-19 16:24:39
FilePath: \script\DataCollectionPC\data_collection.py
'''

import D435i 
import IMU_Microstrain 

IMU_Microstrain.COM_PORT = 'COM5'

Microstrain = IMU_Microstrain.Microstrain_Class(SampleRate=100)
accel_enable = True; gyro_enable = False; euler_enable = True
Microstrain.configIMUChannel(accel_enable,gyro_enable,euler_enable)

# 1. parse PacketNumber packet of the data stream
Microstrain.parseDataStream_Number(200, 1, accel_enable, accel_enable)

# 2. Record data into CSV file
Microstrain.recordDataToCSV(0,1)

# 3. plot data into Figure, and save into a PNG image
Microstrain.plotDataCSV('data_2022-08-13 15:15:25.822028.csv')

# 4. parse packets of the data stream to update the
# latest IMU data into Class properties
Microstrain.parseDataStrean_Loop(200)

Microstrain.setToIdle()
