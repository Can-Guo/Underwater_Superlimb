'''
Date: 2022-07-27 21:47:46
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-07 02:16:52
FilePath: /python/run_robot.py
'''


from Xbox import XBOX_Class 
# from IMU_Microstrain import Microstrain_Class 
# from D435i import D435i_Class 
from T200_Truster import POWER, T200_Class 
from Dynamixel import Servo_Class 

import time 
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


# Thread 2: D435i Camera with IMU


# Thread 3: Microstrain IMU 


# Thread 4: State Estimate 


# Thread 5: T200 and Servo Control based on the Control Command 

def T200_Servo_command(input_queue_1):

    # initial the control library of T200 Thruster
    T200_thruster = T200_Class()
    T200_thruster.T200_power_scale = POWER[3]
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
            servo_left_angle = (int)(command.usrl_servo_command / 360.0 * 4096)
            servo_right_angle = 4095 - servo_left_angle
        elif 0.0 <= command.usrl_servo_command < 180.0:
            servo_left_angle = (int)(command.usrl_servo_command / 360.0 * 4096)
            servo_right_angle = 4095 - servo_left_angle

        print("Left Servo Position: %d \t Right Servo Position: %d" % (servo_left_angle,servo_right_angle))
        Servo.sync_Write_Angle([servo_left_angle,servo_right_angle])

        # print("Power Scale: %f", T200_thruster.T200_power_scale)

        if command.L_step <= -0.99:
            T200_thruster.send_T200_PWM_Width([1500,1500])
        else:
            T200_PWM_Width = (int) (1500 + (command.L_step + 1) * (400) * T200_thruster.T200_power_scale )

            T200_thruster.send_T200_PWM_Width([T200_PWM_Width, T200_PWM_Width])
        print("While is running and sending PWM!")


def main_process():

    global stop_threads
    stop_threads = False

    # Create FIFO Queue for multi-threading
    q1 = Queue()
    t1 = Thread(target = XBOX_monitor, args = (q1,))
    t2 = Thread(target = T200_Servo_command, args = (q1, ))

    t1.start()
    t2.start() 

    return 
    

if __name__ == "__main__":

    main_process()




