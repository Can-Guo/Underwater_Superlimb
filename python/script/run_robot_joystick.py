'''
Date: 2022-07-27 21:47:46
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-02-16 16:35:24
FilePath: /script/run_robot_joystick.py
'''


from socket_imu_command import IMUCommandSocketClass 

Socket_Command = IMUCommandSocketClass()

msgfromClient = "Hello,UDP Server!".encode('utf-8')

serverAddressPort = ("10.12.234.126", 54000)



from Xbox import XBOX_Class 
from IMU_Microstrain import Microstrain_Class 
# from D435i import D435i_Class 
from T200_Truster import POWER, T200_Class 
from Dynamixel import Servo_Class 

import time 
import numpy as np 

from queue import Queue 
from threading import Thread 

import matplotlib.pyplot as plt



# Thread 1: XBOX Joystick
# def XBOX_monitor(xbox_queue_1):

#     XBOX_device = XBOX_Class()
#     XBOX_device.initialize_xbox()
#     print("XBOX Initialization is Successful!")
#     time.sleep(3)

#     while True:
#         command = XBOX_device.get_xbox_status()
#         xbox_queue_1.put(command)

#         if stop_threads == True:
#             break


# Thread 2: Microstrain IMU Recording into CSV file
# def IMU_Microstrain_Record_CSV():
#     accel_enable = True
#     euler_enable = True
#     IMU_Microstrain = Microstrain_Class()#SampleRate=100)
#     IMU_Microstrain.configIMUChannel(accel_enable,0,euler_enable)
#     IMU_Microstrain.recordDataToCSV(accel_enable, euler_enable)
#     print("Recording IMU Data... Please Ctrl + C to terminate the recording.")


# Thread 3: Microstrain IMU Producer for Realtime Plotting and Update
# def IMU_Microstrain_producer(output_queue):
    
#     if Accel_enable == True and Euler_enable == True:
#         imu_list = np.zeros([100,6])
#     elif Accel_enable == False and Euler_enable == True:
#         imu_list = np.zeros([100,3])
    
#     # initialize the IMU class and config the IMU Channel
#     IMU_Microstrain = Microstrain_Class(SampleRate=100)
#     IMU_Microstrain.configIMUChannel(Accel_enable,0,Euler_enable)

#     while True:
#         imu_data_update = IMU_Microstrain.parseDataStream_Number(200,1,Accel_enable, Euler_enable)

#         imu_list[:-1] = imu_list[1:]
#         imu_list[-1] = imu_data_update

#         output_queue.put(imu_list)
#         if stop_threads == True:
#             exit

    # return imu_list
        
# Thread 4:  IMU Data Transmission Thread

# def IMU_Data_Trans(input_queue):
    
#     imu_queue = input_queue.get()

#     return imu_queue


# Thread 5: T200 and Servo Control based on the XBOX Joystick Control Command 

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

    Servo.sync_Write_Angle([0,0])
    print("Initialize the T200 and Servo is Successful!")


    # 1. create socekt and send a hint to client
    Socket_Command.UDPClientSocket.sendto(msgfromClient, serverAddressPort)

    

    # print("IP:{}".format(msgfromServer[1]))

    # print("IMU command %s", msgfromServer[0])

    



    while True:

        msgfromServer = Socket_Command.UDPClientSocket.recvfrom(1024)
        imu_command = msgfromServer[0].decode('utf-8')

        command = imu_command

        # print("Angle:", command.usrl_servo_command)
        if command=='0':
            Servo.sync_Write_Angle([2048,2048])
            T200_thruster.send_T200_PWM_Width([1500,1500])

        elif command == '1':
            left_angle = 1024
        
        elif command == '2':
            left_angle = 0

        elif command == '4':
            left_angle = 3072

        elif command == '5':
            thrust = t                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             bhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhrust - 10

        elif command == '6':
            thrust = thrust + 10

        elif command == '3':
            thrust = 1500
        
        right_angle = 4095 - left_angle

        Servo.sync_Write_Angle([left_angle,right_angle])
        if thrust > 1600:
            thrust = 1600
        elif thrust < 1400:
            thrust = 1400
            
        T200_thruster.send_T200_PWM_Width([thrust,thrust])

        # if 180.0 <= command.usrl_servo_command < 360.0:
        #     servo_left_position = (int)(command.usrl_servo_command / 360.0 * 4096)
        #     servo_right_position = 4095 - servo_left_position
        # elif 0.0 <= command.usrl_servo_command < 180.0:
        #     servo_left_position = (int)(command.usrl_servo_command / 360.0 * 4096)
        #     servo_right_position = 4095 - servo_left_position

        # Servo.sync_Write_Angle([servo_left_position,servo_right_position])
        # # print("Left Servo Position: %d \t Right Servo Position: %d" % (servo_left_position,servo_right_position))

        # # print("Power Scale: %f", T200_thruster.T200_power_scale)

        # if command.L_step <= -0.99 or command.R_step <= -0.99 :
        #     T200_thruster.send_T200_PWM_Width([1500,1500])
        # else:
        #     T200_PWM_Width = (int) (1500 + (command.R_step + 1) * (400) * T200_thruster.T200_power_scale )

        #     T200_thruster.send_T200_PWM_Width([T200_PWM_Width, T200_PWM_Width])
        #     print("PWM %d,While is running and sending PWM!" % T200_PWM_Width)


def main_process():

    # TODO: initialize the IMU data from Microstrain IMU 
    # initialize the IMU data
    # global q_lines; q_lines = []

    # global Accel_enable;Accel_enable = False
    # global Euler_enable;Euler_enable = True
    
    # global imu_list 
    
    # fig = plt.figure(figsize=(12, 6))

    # if Accel_enable == False and Euler_enable == True:
    #     q_init = np.zeros([100,3])
    #     angle_name = ['Roll','Pitch','Yaw']

    #     for i in range(3):
    #         plt.subplot(3,1,i+1)
    #         if i == 0:
    #             q_line, = plt.plot(q_init[:,i],'r-')
    #         elif i == 1:
    #             q_line, = plt.plot(q_init[:,i],'g-')
    #         elif i == 2:
    #             q_line, = plt.plot(q_init[:,i],'b-')

    #         q_lines.append(q_line)
            
    #         plt.ylabel('{}/radian'.format(angle_name[i]))
    #     # plt.ylim([-180,180])

    #     plt.ylim([-np.pi, np.pi])

    #     plt.xlabel('IMU data frames')
    #     fig.legend(['IMU data'],loc='upper center')
    #     fig.tight_layout()
    #     plt.draw()  

    # if Accel_enable == True and Euler_enable == True:
    #     q_init = np.zeros([100,6])
    #     plot_name = ['Accel_x','Accel_y', 'Accel_z', 'Roll','Pitch','Yaw']
        
    #     for i in range(6):
    #         plt.subplot(3,1,i+1)

    #         if i == 0:
    #             q_line, = plt.plot(q_init[:,i],'r--')
    #             plt.ylabel('{}/g'.format(plot_name[i]))
    #         elif i == 1:
    #             q_line, = plt.plot(q_init[:,i],'g--')
    #             plt.ylabel('{}/g'.format(plot_name[i]))
    #         elif i == 2:
    #             q_line, = plt.plot(q_init[:,i],'b--')
    #             plt.ylim([-2,2])
    #             plt.ylabel('{}/g'.format(plot_name[i]))
    #         elif i == 3:
    #             q_line, = plt.plot(q_init[:,i],'r-')
    #             plt.ylabel('{}/radian'.format(plot_name[i]))
    #         elif i == 4:
    #             q_line, = plt.plot(q_init[:,i],'g-')
    #             plt.ylabel('{}/radian'.format(plot_name[i]))
    #         elif i == 5:
    #             q_line, = plt.plot(q_init[:,i],'b-')
    #             plt.ylim([-np.pi, np.pi])
    #             plt.ylabel('{}/radian'.format(plot_name[i]))
            
    #         q_lines.append(q_line)
             
    #     plt.xlabel('IMU data frames')
    #     fig.legend(['IMU data'],loc='upper center')
    #     fig.tight_layout()
    #     plt.draw()  

    # global stop_threads
    # stop_threads = False

    # # Multithread Definition

    # # Create FIFO Queue for multi-threading
    # q1 = Queue()
    t1 = Thread(target = T200_Servo_command)
    # t2 = Thread(target = T200_Servo_command, args = (q1, ))


    # q2 = Queue()
    # t3 = Thread(target=IMU_Microstrain_producer, args=(q2,))
    # t4 = Thread(target=IMU_Data_Trans, args=(q2,))


    # t5 = Thread(target=IMU_Microstrain_Record_CSV)

    # Multithread Executation

    t1.start()
    # t2.start() 
    # 
    # t3.start()
    # t4.start()

    # t5.start()
    
 
    # tick1 = time.time()

    # main Thread to Update the plot of the IMU fixed to the Robot and Body

    # while True:

    #     IMU_list = IMU_Data_Trans(input_queue=q2)

    #     for i in range(IMU_list.shape[1]):
    #         q_lines[i].set_ydata(IMU_list[:,i])

    #     plt.draw()
    #     plt.pause(0.001)

    #     if stop_threads == True:
    #         break
    

if __name__ == "__main__":

    main_process()

