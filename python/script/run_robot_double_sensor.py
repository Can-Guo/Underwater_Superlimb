'''
Date: 2023-02-16 19:38:48
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-02-21 16:01:30
FilePath: /script/run_robot_double_sensor.py
'''

from T200_Truster import POWER, T200_Class 
from Dynamixel import Servo_Class 
import time 
import socket as Socket
# from queue import Queue 
# from threading import Thread 

# from Socket_IMU import IMUSocketClass 

def decodeClient(Data_Server):

    token_list = Data_Server.split(',')

    print("Decoded Data List", token_list)

    return token_list 


def T200_Servo_command():

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
    socket_pi.connect(("10.12.234.126",54000))


    left_angle = 2048
    right_angle = 2048
    thrust = 1500
    
    while(True):

        # IMUSocket_client.UDPClientSocket.sendto(msgFromClient, serverAddressPort)
        # msgFromServer = IMUSocket_client.UDPClientSocket.recvfrom(1024)
        msgFromServer = socket_pi.recv(1024)

        Decoded_List = decodeClient(msgFromServer.decode('utf-8'))

        # print("Double Token: %s ", msgFromServer[0])

        ## Emergency Message!
        if Decoded_List[1] == 'so':
            # play Help.wav on On-land Station
            left_angle = 2048
            right_angle = 2048
            # IMUSocket_client.UDPClientSocket.sendto("Help!SOS!".encode('utf-8'), serverAddressPort)
            print("Help Sent Success!")
            break 
        
        ## Reset Servo and Thrust to default status
        elif Decoded_List[1] == 'fa':
            print("Reset")
            left_angle = 2048
            thrust = 1500

        ## Direction Control
        elif Decoded_List[0] == '3' and Decoded_List[1] == 'me':
            print("forward")
            left_angle = 2048
            right_angle = 2048
            
        elif Decoded_List[0] == '2' and Decoded_List[1] == 'me':
            print("turn left")
            left_angle = 0
            right_angle = 2048
            
        elif Decoded_List[0] == '1' and Decoded_List[1] == 'me':
            print("turning right")
            left_angle = 2048
            right_angle = 1
            
        elif Decoded_List[0] == '5' and Decoded_List[1] == 'me':
            print("Diving Up")
            left_angle = 3072
            right_angle = 1024
            
        elif Decoded_List[0] == '6' and Decoded_List[1] == 'me':
            print("Diving Down")
            left_angle = 1024
            # left_angle = 3072
            right_angle = 3072

        ## Speed Control with PWM value
        elif Decoded_List[0] == '4' and Decoded_List[1] == 'do':
            print("Speed Up")
            thrust = thrust + 30

        elif Decoded_List[0] == '4' and Decoded_List[1] == 're':
            print("Speed Down")
            thrust = thrust - 30

        else:
            pass 

        ## Check servo position command, to avoid Servo Error!
        if left_angle <= 1:
            left_angle = 1
        if left_angle >= 4090:
            left_angle = 4090
            
        if right_angle <= 1:
            right_angle = 1
        if right_angle >= 4090:
            right_angle = 4090
        

        Servo.sync_Write_Angle([left_angle,right_angle])

        ## Check T200 Thruster Control PWM value to avoid danger in LAB!

        if thrust >= 1600:
            thrust = 1600
        elif thrust < 1400:
            thrust = 1400
            
        T200_thruster.send_T200_PWM_Width([thrust,thrust])

        print("Command Sent Final:",left_angle,right_angle, thrust)

if __name__ == '__main__':
    T200_Servo_command()


        
