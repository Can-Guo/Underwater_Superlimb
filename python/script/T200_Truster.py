'''
Date: 2022-07-27 21:48:46
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-14 10:31:22
FilePath: /script/T200_Truster.py
'''

import os
# import commands

import pigpio 
import numpy as np 
import time 

POWER = np.array([0.0, 0.20, 0.40, 0.60, 0.80, 1.00])  ## Power scaler to control the Power of T200 ThrusterPOWER = np.array([0.0, 0.20, 0.40, 0.60, 0.80, 1.00])  ## Power scaler to control the Power of T200 Thruster


class T200_Class:

    def __init__(self) -> None:

        # Before you config, run "sudo pigpiod" in your terminal to start the pigpiod daemon
        password = '123'
        command1 = ' pigpiod'
        command2 = ' killall pigpiod'

        if(self.sudo_command(password, command1) == '0'):
            pass
        else:
            self.sudo_command(password, command2)
            self.sudo_command(password, command1)
        
        # self.sudo_command(password,command1)

        time.sleep(0.1)
    
        self.pi = pigpio.pi()

        self.T200_neutral_position = 1500
        self.T200_range = 2000
        self.T200_pins = np.array([20,21])  # T200 -> 20, 21 PIN of Raspberry Pi 4B
        self.T200_frequency = 100
        self.T200_power_scale = POWER[0]
        self.T200_home_position = np.array([1500,1500])

        # initialize the T200 via PWM control
        self.initialize_T200_PWM()
        # waiting for the T200 Thruster to settle and initialization of the POWER
        time.sleep(3)
    

    def sudo_command(self, password, command):
        # print(os.system('echo %s | sudo -S %s' % (password, command)))
        return os.system('echo %s | sudo -S %s' % (password, command))


    def initialize_T200_PWM(self):
        for i in range(2):
            self.pi.set_PWM_frequency(self.T200_pins[i],self.T200_frequency)
            self.pi.set_PWM_range(self.T200_pins[i],self.T200_range)            
            self.pi.set_servo_pulsewidth(self.T200_pins[i],self.T200_home_position[i])

        print("Initialization of T200 is done! ")
        
        return None


    def send_T200_PWM_Width(self, pulse_width):
        # pulse_width = (pulse_width)

        for i in range(2):
            self.pi.set_servo_pulsewidth(
                self.T200_pins[i], pulse_width[i]
            )


    # TODO: Mapping from force to T200 PWM, lookup Table
    def force_to_T200_PWM(self, force_in_Newton):
        
        pwm_width = force_in_Newton

        return pwm_width
    

#####################
# Test of the T200_Class 
T200 = T200_Class()
T200.send_T200_PWM_Width([1250,1250])


time.sleep(10)
T200.send_T200_PWM_Width([1500,1500])

#####################

    