'''
Date: 2022-07-27 21:47:55
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-04 00:44:05
FilePath: /python/Xbox.py
'''


## Functions of the class:
# This class can 
# 1. initialize the XBOX One Wireless controller 
# 2. access the axis, button & hat status of the joystick 
# 3. access the ID,GUID,name in system, power level of the joystick


import pygame
import numpy as np 


class XBOX_Class(object):
    
    def __int__(self):
        
        # TODO: Define the function of the axes & buttons of the XBOX controlle
        
        # # ID of the joystick
        self.joystick = None
        self.name = None
        self.GUID = None
        self.done = None # Can be used to stop the scanning

        # There are 6 axes in the XBOX joystick controller
        # axis_0,axis_1 --> left  stick
        # axis_3,axis_4 --> right stick
        # axis_2 --> Left trigger
        # axis_5 --> Right trigger
        
        self.axis_0 = 0.
        self.axis_1 = 0.
        self.L_step = -1.
        self.axis_3 = 0.
        self.axis_4 = 0.
        self.R_step = -1.

        self.usrl_servo_command = 0.0



        # number of axes, buttons, hat(s)
        self.axes = 0.
        self.buttons = 0.
        self.hats = 0.


    def initialize_xbox(self):
        # Initialize the pyname module
        pygame.init()

        # Initialize the joystick sub-module
        pygame.joystick.init()

        # initialize the clock block
        # clock = pygame.time.Clock()

        # Initialize the joystick No.1, can integrated with more than 1 joystick
        joystick_count = pygame.joystick.get_count()

        if joystick_count == 0 :
            print("No Joystick is connected!")
            

        elif joystick_count >=1 :
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.name = self.joystick.get_name()

            print("Joystick ID : ",self.joystick)
            print("The Name of the Joystick : ",self.name)
            
        # elif joystick_count >= 2 :
            # print("The XBOX class has no compatible with more than 1 joystick, yet!")
            
        
        # Get the number of axes
        self.axes = self.joystick.get_numaxes()
        print("Number of axes:", self.axes)

        # Get the number of the buttons
        self.buttons = self.joystick.get_numbuttons()
        print("Number of buttons:",self.buttons)
        
        # Get the number of the hats
        self.hats = self.joystick.get_numhats()
        print("Number of hats:", self.hats)

        # Get the power level of the joystick
        # self.power = self.joystick.get_power_level()
        # print("Power Level : " , self.power)
        # There are 11 buttons in the XBOX joystick controller
        
        self.A = 0.
        self.B = 0.
        self.X = 0.
        self.Y = 0.
        self.LB = 0.
        self.RB = 0.
        self.Share = 0.
        self.Menu = 0.
        self.Disonnect = 0.
        self.LeftStickPress = 0
        self.RightStickPress = 0

        # There is only one hat (0,0) in the XBOX joystick controller

        # hat_0 = (-1, 0) --> FX_left
        # hat_0 = (0 ,-1) --> FX_down
        # hat_0 = (0 , 1) --> FX_up
        # hat_0 = (1 , 0) --> FX_right
        
        self.FX_right = 0.
        self.FX_left = 0.
        self.FX_up = 0.
        self.FX_down = 0.
        self.FX_default = 0.

        # Get the GUID of the joystick
        self.GUID = self.joystick.get_guid()
        print("GUID of the XBOX : " , self.GUID)
        print("Initialization of the XBOX is done!")
    

    def clear_xbox_status(self):

        self.A = 0.
        self.B = 0.
        self.X = 0.
        self.Y = 0.
        self.LB = 0.
        self.RB = 0.
        self.Share = 0.
        self.Menu = 0.
        self.Disonnect = 0.
        self.LeftStickPress = 0
        self.RightStickPress = 0

        self.FX_right = 0.
        self.FX_left = 0.
        self.FX_up = 0.
        self.FX_down = 0.
        self.FX_default = 0.

        self.axis_0 = 0.
        self.axis_1 = 0.
        self.L_step = -1.
        self.axis_3 = 0.
        self.axis_4 = 0.
        self.R_step = -1.

        
    def get_xbox_status(self):

        self.done = False

        if self.done == False:
            ## TODO: need to integrate with the stepless abjustment of Power 

            ### HAHAHA ! Interesting ! 


            clock = pygame.time.Clock()
            
            
            # while self.done == False:
                
            # self.initialize_xbox()
            # EVENT PROCESSING STEP
            # if pygame.event.get() == None:
            
            self.clear_xbox_status()
                
            for event in pygame.event.get(): # User did something
                if event.type == pygame.QUIT: # If user clicked close
                    # self.done=True # Flag that we are done so we exit this loop
                    pygame.quit()
                    exit()
            
            # Get the status of the axes
            for i in range( self.axes ):
                axis = self.joystick.get_axis( i )
                # print(self.axes)
                if i == 0:
                    self.axis_0 = axis
                    # print("0:",self.axis_0)
                if i == 1:
                    self.axis_1 = axis
                    # print("1:",self.axis_1)
                if i == 2:
                    self.L_step = axis
                    # print("2:",self.L_step)
                if i == 3:
                    self.axis_3 = axis
                    # print("3:",self.axis_3)
                if i == 4:
                    # print(i)
                    self.axis_4 = axis
                    # print("4:",self.axis_4)
                    # print("R Step:",self.R_step)
                if i == 5:
                    self.R_step = axis
                    # print("L Step  ",self.L_step)

            # print("Stick 1  (%f,%f)  \n" % (self.axis_0, self.axis_1))
            # print(" Left_Step  %f  \n" % self.L_step)
            # print("Stick 2  (%f,%f)  \n" % (self.axis_3, self.axis_4))
            # print("Right_Step  %f  \n" % self.R_step)


            # Get the status of the buttons
            for i in range( self.buttons ):
                button = self.joystick.get_button( i )
                # print(i,button)
                if i == 0 and button == 1:
                    self.A = 1
                    self.B = 0
                    self.X = 0
                    self.Y = 0
                    print("A")

                if i == 1 and button == 1:
                    self.A = 0
                    self.B = 1
                    self.X = 0
                    self.Y = 0
                    print("B")

                if i == 2 and button == 1:
                    self.A = 0
                    self.B = 0
                    self.X = 1
                    self.Y = 0
                    print("X")

                if i == 3 and button == 1:
                    self.A = 0
                    self.B = 0
                    self.X = 0
                    self.Y = 1
                    print("Y")

                if i == 4 and button == 1:
                    self.LB = 1.0
                    print("LB")

                if i == 5 and button == 1:
                    self.RB = 1.0
                    print("RB")

                if i == 6 and button == 1:
                    self.Disonnect = 1.0
                    # self.done = True
                    # print("Stop Connection !")
                    # self.shutdown()

                if i == 7 and button == 1:
                    self.Menu = 1
                    print("Menu")

                if i == 8 and button == 1:
                    print("POWER Button!")
                    # print(i)

                if i == 9 and button == 1:
                    self.LeftStickPress = 1
                    print("Left Stick Pressed")

                if i == 10 and button == 1:
                    self.RightStickPress = 0
                    print("Right Stick Pressed")
                    


            for i in range( self.hats ):
                hat = self.joystick.get_hat( i )
                # print(hat)
                if hat == (1,0):
                    self.FX_right = 1.0
                    print("FX_right")
                if hat == (-1,0):
                    self.FX_left = 1.0
                    print("FX_left")
                if hat == (0,1):
                    self.FX_up = 1.0
                    print("FX_up")
                if hat == (0,-1):
                    self.FX_down = 1.0
                    print("FX_down")
                if hat == (0,0):
                    self.FX_default = 1.0
            
            self.usrl_servo_command = self.usrl_servo_angle(self.axis_0, self.axis_1)
                    
                    
            # clock.tick(10)
        
        # return self.axis_0, self.axis_1
        return self


    def usrl_servo_angle(self, axis_0, axis_1):
        '''
        input: two axes of the joy stick, range [-1,1] for each axis, digital number
        output: Expected angle of the two servos of USRL, range [0,360], /degree
        '''

        axis_0_mode = np.abs(axis_0)
        axis_1_mode = np.abs(axis_1)
        
        
        if np.abs(axis_0) < 0.1 and np.abs(axis_1) < 0.1:
            value = 0
            angle = 0

        elif (np.abs(axis_0) < 0.1 and np.abs(axis_1) > 0.98):
            if (axis_1) > 0:
                angle = np.pi/2
            else:
                angle = 3*np.pi/2
                
        elif (np.abs(axis_0) > 0.98 and np.abs(axis_1) < 0.1):
            if (axis_0) > 0:
                angle = np.pi
            else:
                angle = 0.0

        else:
            value = (axis_1_mode/axis_0_mode)
            angle = 0
        
            if axis_0 > 0 and axis_1 > 0:
                angle = np.arctan(1/value) + np.pi/2
            elif axis_0 < 0 and axis_1 > 0:
                angle = np.arctan(value) + 0.0
            elif axis_0 > 0 and axis_1 < 0:
                angle = np.arctan(value) + np.pi
            elif axis_0 < 0 and axis_1 < 0:
                angle = - np.arctan(value) + 2*np.pi

        Angle = int(angle*180/np.pi)
        # print("Resove angle %d deg", Angle)

        return Angle


    def shutdown(self):
        if self.done == True:
            pygame.joystick.quit()
            pygame.quit()
            exit()


##########################
# Test the Xbox class module.

# xbox = XBOX_Class()
# xbox.initialize_xbox()
# while True:
#     xbox.get_xbox_status()

# Test End.
##########################