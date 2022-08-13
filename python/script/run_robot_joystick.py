'''
Date: 2022-07-27 21:47:46
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-12 19:48:15
FilePath: /Underwater_Superlimb/python/script/run_robot_joystick.py
'''


from os import times
from Xbox import XBOX_Class 
# from IMU_Microstrain import Microstrain_Class 
# from D435i import D435i_Class 
from T200_Truster import POWER, T200_Class 
from Dynamixel import Servo_Class 

import time 
import numpy as np 

from queue import Queue 
from threading import Thread 

import matplotlib.pyplot as plt 


# Thread 1: XBOX Joystick
def XBOX_monitor(xbox_queue_1):

    XBOX_device = XBOX_Class()
    XBOX_device.initialize_xbox()
    print("XBOX Initialization is Successful!")
    time.sleep(3)

    while True:
        command = XBOX_device.get_xbox_status()
        xbox_queue_1.put(command)

        if stop_threads == True:
            break


# Thread 2: D435i Camera with IMU Producer


# Thread 3: Microstrain IMU Producer


# Thread 4: State Estimate


# Thread 5: T200 and Servo Control based on the XBOX Joystick Control Command 

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

    # TODO: initialize the IMU data from Microstrain IMU 
    # initialize the IMU data
    global q_lines

    global Accel_enable;Accel_enable= False
    global Euler_enable;Euler_enable = True
    
    fig = plt.figure(figsize=(20, 10))

    if Accel_enable == False and Euler_enable == True:
        q_init = np.zeros([1000,3])
        angle_name = ['Roll','Pitch','Yaw']

        for i in range(3):
            plt.subplot(3,1,i+1)
            if i == 0:
                q_line, = plt.plot(q_init[:,i],'r-')
            elif i == 1:
                q_line, = plt.plot(q_init[:,i],'b-')
            elif i == 2:
                q_line, = plt.plot(q_init[:,i],'g-')
                
            q_lines.append(q_line)
            plt.ylabel('{}/deg'.format(angle_name[i]))
            plt.ylim([-180,180])

        plt.xlabel('IMU data frames')
        fig.legend(['IMU data'],loc='upper center')
        fig.tight_layout()
        plt.draw()  

    if Accel_enable == True and Euler_enable == True:
        pass


    global stop_threads
    stop_threads = False

    # Create FIFO Queue for multi-threading
    q1 = Queue()
    t1 = Thread(target = XBOX_monitor, args = (q1,))
    t2 = Thread(target = T200_Servo_command, args = (q1, ))

    t1.start()
    t2.start() 



    tick1 = time.time()

    while True:
        angle = 

    return 
    

if __name__ == "__main__":

    main_process()




