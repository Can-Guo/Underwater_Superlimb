'''
Date: 2023-01-11 21:55:26
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-01-12 00:19:58
FilePath: /script/IMU_Record.py
'''

################################################
# Thread 1: Access IMU data from Microstrain IMU sensor
# Thread 2: plot IMU data in realtime
# Thread 3: record IMU data into CSV file
################################################


import numpy as np 
from queue import Queue 
from threading import Thread 
import matplotlib.pyplot as plt 
import scienceplots 
from IMU_Microstrain import Microstrain_Class

## IMU class Initialization
IMU_Class = Microstrain_Class(100)
accel_enable = True
euler_enable = True
IMU_Class.configIMUChannel(accel_enable,0,euler_enable)

imu_list = np.zeros([100,6])
global q_lines;
q_lines = []

## Thread 3: record IMU data into CSV file 
def Record_IMU():
    accel_enable = True
    euler_enable = True
    IMU_Class.recordDataToCSV(accel_enable, euler_enable)


## Thread 1: Access IMU data from Microstrain IMU sensor
def Access_IMU(imu_output_queue_1):

    while True:
        imu_data_update = IMU_Class.parseDataStream_Number(200, 1, 1, 1)
        
        imu_list[:-1] = imu_list[1:]
        imu_list[-1] = imu_data_update
        imu_output_queue_1.put(imu_list)


## Thread 2: plot IMU data in realtime

def Return_IMU(imu_input_queue_1):
    imu_queue = imu_input_queue_1.get()
    # pass 
    return imu_queue 
    
        
## Multi-thread Definition
# Create FIFO Queue for multi-threading
q1= Queue()
t1 = Thread(target = Access_IMU, args=(q1,))
t2 = Thread(target=Return_IMU, args=(q1,))

# t3 = Thread(target=Record_IMU)

t1.start()
t2.start()
# t3.start()


## Main Thread for Matplotlig GUI 

fig = plt.figure(figsize = (20,14))

q_init = np.zeros([100,6])
plot_name = ['Accel_x','Accel_y','Accel_z','Roll', 'Pitch','Yaw']
color_list = ['r--','g--','b--','r-','g-','b-']

for i in range(6):
    plt.subplot(6,1,i+1)
    q_line, = plt.plot(q_init[:,i],color_list[i])
    plt.ylabel('{}'.format(plot_name[i]))
    q_lines.append(q_line)

plt.xlabel('IMU Data Frame')
fig.tight_layout()
plt.draw()  

while True:
    imu_plot_list = Return_IMU(imu_input_queue_1= q1)
    for i in range(6):
        q_lines[i].set_ydata(imu_plot_list[:,i])
    plt.draw()
    