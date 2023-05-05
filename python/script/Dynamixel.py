'''
Date: 2022-07-27 21:48:24
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-05-05 09:24:29
FilePath: /script/Dynamixel.py
'''


import os
from turtle import left 
import numpy as np 

if os.name == 'nt':
    import msvcrt 
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios 
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:

            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch 
    

from dynamixel_sdk import * 

MY_DXL = 'X_SERIES'

if MY_DXL == 'X_SERIES':
    ADDR_TORQUE_ENABLE          = 64
    ADDR_GOAL_POSITION          = 116
    LEN_GOAL_POSITION           = 4         # Data Byte Length
    ADDR_PRESENT_POSITION       = 132
    LEN_PRESENT_POSITION        = 4         # Data Byte Length
    DXL_MINIMUM_POSITION_VALUE  = 0         # Refer to the Minimum Position Limit of product eManual
    DXL_MAXIMUM_POSITION_VALUE  = 4095      # Refer to the Maximum Position Limit of product eManual
    BAUDRATE                    = 57600


# DYNAMIXEL Protocol Version (1.0 / 2.0)
# https://emanual.robotis.com/docs/en/dxl/protocol2/

PROTOCOL_VERSION            = 2.0

TORQUE_ENABLE               = 1                 # Value for enabling the torque
TORQUE_DISABLE              = 0                 # Value for disabling the torque
DXL_MOVING_STATUS_THRESHOLD = 20                # Dynamixel moving status threshold


class Servo_Class(object):

    def __init__(self, PortName, BaudRate) -> None:

        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        self.portHandler = PortHandler(PortName)
        
        # Initialize PacketHandler instance
        # Set the protocol version
        # Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)

        # Initialize GroupSyncWrite instance
        self.groupSyncWrite = GroupSyncWrite(self.portHandler, self.packetHandler, ADDR_GOAL_POSITION, LEN_GOAL_POSITION)

        # Initialize GroupSyncRead instace for Present Position
        self.groupSyncRead = GroupSyncRead(self.portHandler, self.packetHandler, ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)


        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port!")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()

        # Set port baudrate
        if self.portHandler.setBaudRate(BaudRate):
            print("Succeeded to change the baudrate!")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()

        self.DXL_ID_State, dxl_comm_result = self.packetHandler.broadcastPing(self.portHandler)
        self.DXL_ID_List = list(self.DXL_ID_State.keys())

        self.dxl_ID_present_Angle = {self.DXL_ID_List[0]:[],self.DXL_ID_List[1]:[]}

        # Try to broadcast ping the Dynamixel
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))

        print("Ping Successfully! Detected Dynamixel :")

        for dxl_id in self.DXL_ID_List:
            print("[ID:%03d] model version : %d | firmware version : %d" % (dxl_id, self.DXL_ID_State.get(dxl_id)[0], self.DXL_ID_State.get(dxl_id)[1]))

    
    def reboot_Servo(self):
        # Try to reboot
        # Dynamixel LED will flicker while it reboots
        for dxl_id in self.DXL_ID_List:
            dxl_comm_result, dxl_error = self.packetHandler.reboot(self.portHandler, dxl_id)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))
                print("Dynamixel Servo [ID:%03d] reboot Succeeded\n" % dxl_id)
        

    def enable_Torque(self):
        for dxl_id in self.DXL_ID_List:
        # Enable Dynamixel Torque
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            else:
                print("Dynamixel #%d Torque Enabled Successfully!" % dxl_id)
                # print("Dynamixel #%d has been successfully connected" % dxl_id)


    def disable_Torque(self):
        for dxl_id in self.DXL_ID_List:
            # Enable Dynamixel Torque
            dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(self.portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE)
            if dxl_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            elif dxl_error != 0:
                print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            else:
                print("Dynamixel #%d Torque Disabled Successfully!" % dxl_id)
                # print("Dynamixel #%d has been successfully connected" % dxl_id)


    def degree_position(self,degree_list):
        if -180 <= degree_list[0] <= 180:
            left_position = (int)((degree_list[0]*2047/180) + 2047)
        # elif degree_list[0]==-180 and current_angle < 0:
            # left_position = 
        else:
            print("Left Angle [%d] is not valid, please check your angle value!" % degree_list[0])
            
        if -180 <= degree_list[1] <= 180:
            right_position = (int)((-degree_list[1]*2047/180) + 2047)
        else:
            print("Right Angle [%d] is not valid, please check your angle value!" % degree_list[1])
        
        if left_position >= 4095:
            left_position=4095

        if right_position >= 4095:
            right_position=4095
            
        return [left_position,right_position]


    def position_degree(self,position_list):
        
        if position_list[0] >= 4095:
            position_list[0]=4095
        if position_list[1] >= 4095:
            position_list[1]=4095
    
        if 0 <= position_list[0] <= 4095:
            left_angle = 180 * (position_list[0] - 2047) / 2047
        else:
            print("Left Position [%d] is invalid, please check your servo position!" % position_list[0])
            return 

        if 0 <= position_list[1] <= 4095:
            right_angle = -180 * (position_list[1] - 2047) / 2047
        else:
            print("Left Position [%d] is invalid, please check your servo position!" % position_list[1])
            return

        # if 
        return [left_angle,right_angle]


    def sync_Write_Angle(self, dxl_goal_Angle):

        # index = 2
        dxl_goal_position = self.degree_position(dxl_goal_Angle)
        
        # Allocate goal position value into byte array
        for dxl_id in self.DXL_ID_List:
            param_goal_position = [DXL_LOBYTE(DXL_LOWORD(dxl_goal_position[dxl_id-1])), DXL_HIBYTE(DXL_LOWORD(dxl_goal_position[dxl_id-1])), DXL_LOBYTE(DXL_HIWORD(dxl_goal_position[dxl_id-1])), DXL_HIBYTE(DXL_HIWORD(dxl_goal_position[dxl_id-1]))]
            # Add Dynamixel #1 & #2 goal position value to the Syncwrite parameter storage
            dxl_addparam_result = self.groupSyncWrite.addParam(dxl_id, param_goal_position)
            if dxl_addparam_result != True:
                print("[ID:%03d] groupSyncWrite addparam failed" % dxl_id)
                quit()

        # Syncwrite goal position
        dxl_comm_result = self.groupSyncWrite.txPacket()
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))

        # Clear syncwrite parameter storage
        self.groupSyncWrite.clearParam()

        return 

        
    def sync_Read_Angle(self):
        
        # Add parameter storage for Dynamixel#1 present position value
        for dxl_id in self.DXL_ID_List:
            dxl_addparam_result = self.groupSyncRead.addParam(dxl_id)
            if dxl_addparam_result != True:
                print("[ID:%03d] groupSyncRead addparam failed" % dxl_id)
                quit()

            # # Add parameter storage for Dynamixel#2 present position value
            # dxl_addparam_result = groupSyncRead.addParam(DXL2_ID)
            # if dxl_addparam_result != True:
            #     print("[ID:%03d] groupSyncRead addparam failed" % DXL2_ID)
            #     quit()

        

        # Syncread present position
        dxl_comm_result = self.groupSyncRead.txRxPacket()
        
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))

        # for dxl_id in self.DXL_ID_List:

        # Check if groupsyncread data of Dynamixel#1 is available
        dxl_getdata_result = self.groupSyncRead.isAvailable(self.DXL_ID_List[0], ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        
        if dxl_getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % self.DXL_ID_List[0])
            quit()

        dxl_getdata_result = self.groupSyncRead.isAvailable(self.DXL_ID_List[1], ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        
        if dxl_getdata_result != True:
            print("[ID:%03d] groupSyncRead getdata failed" % self.DXL_ID_List[1])
            quit()

        dxl_present_position_1 = self.groupSyncRead.getData(self.DXL_ID_List[0], ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)
        dxl_present_position_2 = self.groupSyncRead.getData(self.DXL_ID_List[1], ADDR_PRESENT_POSITION, LEN_PRESENT_POSITION)

        dxl_present_angle = self.position_degree([dxl_present_position_1,dxl_present_position_2])

        self.dxl_ID_present_Angle[self.DXL_ID_List[0]] = round(dxl_present_angle[0],3)
        self.dxl_ID_present_Angle[self.DXL_ID_List[1]] = round(dxl_present_angle[1],3)

        # print(self.dxl_ID_present_position)
        self.groupSyncRead.clearParam()
        return [round(dxl_present_angle[0],3),round(dxl_present_angle[1],3)]



############################################

# PortName = '/dev/ttyUSB0'
# Servo = Servo_Class(PortName, 57600)

# Servo.enable_Torque()
# Servo.sync_Write_Angle([-90,-110])

# time.sleep(1)
# for i in range(50):
#     Servo.sync_Read_Angle()
#     print("Servo Angle ID 1: %.3f \t ID 2: %.3f" % (Servo.dxl_ID_present_Angle[1],Servo.dxl_ID_present_Angle[1]))

# time.sleep(2)

# Servo.sync_Write_Angle([0,0])

# time.sleep(2)

# Servo.sync_Write_Angle([180,-180])

# for i in range(50):
#     Servo.sync_Read_Angle()
#     print("Servo Angle ID 1: %.3f \t ID 2: %.3f" % (Servo.dxl_ID_present_Angle[1],Servo.dxl_ID_present_Angle[1]))

# dxl_1,dxl_2,dxl_3 = Servo.packetHandler.read1ByteTxRx(Servo.portHandler,1,70)
# print("Error:",dxl_1,dxl_2,dxl_3)

# time.sleep(2)
# Servo.sync_Write_Angle([0,0])
# time.sleep(1)
# Servo.disable_Torque()

############################################
