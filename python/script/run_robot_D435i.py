'''
Date: 2022-08-13 15:17:50
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-13 15:49:47
FilePath: /python/script/run_robot_D435i.py
'''

from IMU_Microstrain import Microstrain_Class 
from D435i import D435i_Class 
from T200_Truster import POWER, T200_Class 
from Dynamixel import Servo_Class 

import time 
import numpy as np 

from queue import Queue 
from threading import Thread 

import matplotlib.pyplot as plt

from .run_robot_joystick import Accel_enable


# Thread 1: Microstrain IMU Recording into CSV file
def IMU_Microstrain_Record_CSV():
    accel_enable = True
    euler_enable = True
    IMU_Microstrain = Microstrain_Class()#SampleRate=100)
    IMU_Microstrain.configIMUChannel(accel_enable,0,euler_enable)
    IMU_Microstrain.recordDataToCSV(accel_enable, euler_enable)
    print("Recording IMU Data... Please Ctrl + C to terminate the recording.")


# Thread 2: D435i IMU information Producer, push into Thread 3
def D435i_IMU_Producer(d435i_queue_1):
    D435i_device = D435i_Class()
    print("D435i Thread is Ready!\r\n")
    while True:
        imu_command = D435i_device.get_IMU_update_Pose()
        d435i_queue_1.put(imu_command)

        if stop_threads == True:
            break


# Thread 3: T200 and Servo Control Based on the the motion information from IMU inside D435i
def T200_Servo_command(input_queue_1):

    # initial the control library of T200 Thruster
    T200_thruster = T200_Class()
    T200_thruster.T200_power_scale = POWER[1]
    T200_thruster.send_T200_PWM_Width([1500, 1500])
    print("Initilize the T200 ...")


    # initial the control SDK of Dynamixel XW540-T140-R servo
    PortName = '/dev/ttyUSB0'
    Servo = Servo_Class(PortName, 57600)                             
    Servo.enable_Torque()
    time.sleep(1)

    Servo.sync_Write_Angle([0,0])
    print("Initialize the T200 and Servo is Successful!")


    while True:

        command = input_queue_1.get()

        print("Angle:", command.usrl_servo_command)

        if 180.0 <= command.usrl_servo_command < 360.0:
            servo_left_position = (int)(command.usrl_servo_command / 360.0 * 4096)
            servo_right_position = 4095 - servo_left_position
        elif 0.0 <= command.usrl_servo_command < 180.0:
            servo_left_position = (int)(command.usrl_servo_command / 360.0 * 4096)
            servo_right_position = 4095 - servo_left_position

        print("Left Servo Position: %d \t Right Servo Position: %d" % (servo_left_position,servo_right_position))
        Servo.sync_Write_Angle([servo_left_position,servo_right_position])

        # print("Power Scale: %f", T200_thruster.T200_power_scale)

        if command.L_step <= -0.99 or command.R_step <= -0.99 :
            T200_thruster.send_T200_PWM_Width([1500,1500])
        else:
            T200_PWM_Width = (int) (1500 + (command.L_step +  command.R_step + 2) * (400) * T200_thruster.T200_power_scale )

            T200_thruster.send_T200_PWM_Width([T200_PWM_Width, T200_PWM_Width])
        print("While is running and sending PWM!")


def main_process():
    # global Stop Flag 
    global stop_threads
    stop_threads = False

    # 
    global Accel_enable; Accel_enable = True
    


