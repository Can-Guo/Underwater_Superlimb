'''
Date: 2023-02-21 14:26:07
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-02-21 17:04:55
FilePath: /script/run_robot_double_stepless_1.py
'''

from turtle import left
from T200_Truster import POWER, T200_Class 
from Dynamixel import Servo_Class 
import time 
import socket as Socket


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

print("Initialize the T200 and Servo is Successful!")


## 1. initialize the UDP communication 
# msgFromClient       = "Hello, UDP Server!".encode('utf-8')
# serverAddressPort   = ("10.12.234.126", 54000)
# IMUSocket_client = IMUSocketClass(serverAddressPort[0],serverAddressPort[1],0)
socket_pi = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
socket_pi.settimeout(5000)
socket_pi.connect(("10.12.234.126",3388))


def decodeClient(Data_Server):

    accel_euler_list = Data_Server.split(',')

    print("Decoded Data List", accel_euler_list)

    return accel_euler_list 


def T200_Servo_command():
    
    print("Begin Servo Control")

    msgFromServer = socket_pi.recv(1024)
    Decoded_euler_List = decodeClient(msgFromServer.decode('utf-8'))

    roll_calib = float(Decoded_euler_List[3])
    pitch_calib = float(Decoded_euler_List[4])
    yaw_calib = float(Decoded_euler_List[5])
    
    print("Roll: %f Pitch: %f Yaw: %f" % (roll_calib, pitch_calib, yaw_calib))

    print("Begin X axis!")
    time.sleep(2)

    i = 0
    left_angle = 2048
    last_roll = roll_calib
    last_yaw = yaw_calib


    while(i<=1000):

        msgFromServer = socket_pi.recv(1024)
        Decoded_euler_List = decodeClient(msgFromServer.decode('utf-8'))
        left_angle = (int) (((float(Decoded_euler_List[3]) - last_roll) / 60) * 1024) + left_angle

        if(left_angle <= 0):
            left_angle = 0
        elif(left_angle>=4090):
            left_angle = 4090

        # print("Roll %s, Left Position: %s"%(Decoded_euler_List[3],left_angle))

        right_angle = (int)(4095- left_angle)

        if(right_angle <= 0):
            right_angle = 0
        elif(right_angle>=4090):
            right_angle = 4090

        Servo.sync_Write_Angle([left_angle, right_angle])
        i = i + 1

        last_roll = float(Decoded_euler_List[3])

        time.sleep(0.04)

    print("Begin Y axis!")
    time.sleep(2)

    # print("Begin Y axis!")
    
    
    # while(i<=500):

    #     msgFromServer = socket_pi.recv(1024)
    #     Decoded_euler_List = decodeClient(msgFromServer.decode('utf-8'))
    #     left_angle = (int) (((float(Decoded_euler_List[4]) - last_yaw) / 60) * 1024) + left_angle

    #     if(left_angle <= 0):
    #         left_angle = 0
    #     elif(left_angle>=4090):
    #         left_angle = 4090

    #     # print("Roll %s, Left Position: %s"%(Decoded_euler_List[3],left_angle))

    #     # right_angle = (int)(4095- left_angle)

    #     # if(right_angle <= 0):
    #     #     right_angle = 0
    #     # elif(right_angle>=4090):
    #     #     right_angle = 4090

    #     Servo.sync_Write_Angle([left_angle, left_angle])
    #     i = i + 1

    #     last_yaw = float(Decoded_euler_List[3])

    #     time.sleep(0.04)



if __name__ == '__main__':
    T200_Servo_command()


