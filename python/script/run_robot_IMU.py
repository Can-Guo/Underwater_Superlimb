'''
Date: 2023-02-16 04:19:47
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-02-16 19:36:59
FilePath: /script/run_robot_IMU.py
'''


from T200_Truster import POWER, T200_Class 
from Dynamixel import Servo_Class 
import time 
import socket as Socket
# from queue import Queue 
# from threading import Thread 

from Socket_IMU import IMUSocketClass 

# global Mi_command1
# global Mi_command2


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

    # # # Servo.sync_Write_Angle([0,0])
    print("Initialize the T200 and Servo is Successful!")

    # print("IP:{}".format(msgfromServer[1]))

    # print("IMU command %s", msgfromServer[0])

    
    # s=Socket.socket(Socket.AF_INET,Socket.SOCK_STREAM)
    # #连接服务器
    # s.connect(("10.13.228.137",7788))
    # global Mi_command1
    # global Mi_command2
    # print("Initialize is done!")

    ## 1. initialize the UDP communication 
    msgFromClient       = "Hello, UDP Server".encode('utf-8')
    serverAddressPort   = ("10.12.234.126", 54000)
    IMUSocket_client = IMUSocketClass(serverAddressPort[0],serverAddressPort[1],0)

    # IMUSocket_client.UDPClientSocket.sendto(msgFromClient, serverAddressPort)
    # msgFromServer = IMUSocket_client.UDPClientSocket.recvfrom(1024)
    # print("Server IP Address:{}".format(msgFromServer[1]))

    left_angle = 2048
    right_angle = 2048
    thrust = 1500
    
    while(True):

        # recvData=s.recv(1024)
        IMUSocket_client.UDPClientSocket.sendto(msgFromClient, serverAddressPort)
        msgFromServer = IMUSocket_client.UDPClientSocket.recvfrom(1024)
        print("IMU Token: %s ",msgFromServer[0].decode('utf-8'))
        
        # print("Data2:",recvData)
        # if(recvData!=[]):
        #     Mi_command1=recvData.decode('utf-8')
        #     time.sleep(0.5)

        #     recvData2=s.recv(1024)
        #     # print("Data2:",recvData2)
            
        #     if(recvData2!=[]):
        #         Mi_command2=recvData2.decode('utf-8')

        #         print("Mi_command:%s | %s" % (Mi_command1, Mi_command2))

        #         ## abjust the Servo Angle Position and T200 PWM value based on the Throat Message

        #         if Mi_command1=='do' and Mi_command2=='re':
        #             #forward
        #             print("Forward!")
        #             left_position = 2048
        #         elif Mi_command1=='re' and Mi_command2=='do':
        #             #backward
        #             print("Backward!")
        #             left_position = 0
        #         elif Mi_command1=='do' and Mi_command2=='me':
        #             #left
        #             print("Left")
        #             left_position = 2048
        #             right_position = 0
        #         elif Mi_command1=='me' and Mi_command2=='do':
        #             #right
        #             print("Right")
        #             left_position = 0
        #             right_position = 2048
        #         elif Mi_command1=='do' and Mi_command2=='so':
        #             #up
        #             print("Up")
        #             left_position = (int)((2048 + 3072)/2)
        #         elif Mi_command1=='so' and Mi_command2=='do':
        #             #down
        #             print("Down")
        #             left_position = (int)((2048 + 1024)/2)
        #         elif Mi_command1=='me' and Mi_command2=='fa':
        #             #speed up
        #             # thrust = thrust + 25
        #             print("Speed Up")

        #         elif Mi_command1=='fa' and Mi_command2=='me':
        #             #speed down
        #             # thrust = thrust - 25
        #             print("Speed Down")
        #         elif Mi_command1=='fa' and Mi_command2=='so':
        #             #stop thruster
        #             # thrust = 1500
        #             print("Stop Thruster")
                    
        #         elif Mi_command1=='so' and Mi_command2=='fa':
        #             #help
        #             print("HELP! EMERGENCY!")
        #             # thrust = 1500
                
        #         ## send control command to servo and T200 Thruster
        #         # Servo.sync_Write_Angle([left_position,right_position])
        #         # T200_thruster.send_T200_PWM_Width([thrust,thrust])
        #         Mi_command1=['']
        #         Mi_command2=['']
                
                
        #     else:
        #         time.sleep(0.5)
        #         Mi_command1=['']
        #         Mi_command2=['']
        #         continue 
        # else:
        #     time.sleep(0.5)
        #     Mi_command1=['']
        #     Mi_command2=['']
        #     continue 
            

        command = str(msgFromServer[0].decode('utf-8'))
        print("Current Mode:",command)
        
        # print("Angle:", command.usrl_servo_command)
        if command=='1':
            # right
            left_angle = 2048
            right_angle = 0

        elif command == '2':
            # left
            left_angle = 0
            right_angle = 2048
        
        elif command == '3':
            # angle increase
            if (left_angle + 1023 >= 4095):
                left_angle = 4094
            else:
                left_angle = left_angle + 1023
            right_angle = 4095 - left_angle

        elif command == '4':
            # angle decrease
            if (left_angle - 1023 <= 0):
                left_angle = 1
            else:
                left_angle = left_angle - 1023
            right_angle = 4095 - left_angle

        elif command == '5':
            # PWM increase
            thrust = thrust - 25


        elif command == '6':
            # PWM decrease
            thrust = thrust + 25

        
        # right_angle = 4095 - left_angle

        Servo.sync_Write_Angle([left_angle,right_angle])

        if thrust >= 1575:
            thrust = 1575
        elif thrust < 1425:
            thrust = 1425
            
        T200_thruster.send_T200_PWM_Width([thrust,thrust])
        print("Command:",left_angle,right_angle, thrust)


if __name__ == '__main__':
    T200_Servo_command()

