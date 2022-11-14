'''
Date: 2022-09-14 16:27:54
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-09-14 18:54:10
FilePath: \Underwater_Superlimb\python\script\remote_keyboard_server.py
'''

from http import server
import keyboard 
import socket

# input : keyboard operation by user on Server (PC on land)
# output: keyvalue which is pressed by user, send to Client (RaspberryPi underwater)

class KeyboardSocketClass(object):

    def __init__(self, local_ip = "169.254.11.229", local_port=6500, server_or = 1):
        self.server_or = server_or

        self.serverAddressport=(local_ip, local_port)
        self.msgFromClient = "Hello, UDP Server. This is Client from RaspberryPi underwater!".encode('utf-8')

        try:
            self.UDPServerSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.UDPClientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            if self.server_or == 0:
                ## Server
                self.UDPServerSocket.bind(local_ip, local_port)
                print("Socket Server Initialization is Successful!\r\n")
            
            elif self.server_or == 0:
                
                ## Client -- RaspberryPi underwater
                ## initialize the KEYBOARD value

                ## For Angle Control
                self.Q = 0 # Angle -- 0
                self.W = 0 # Angle -- 90
                self.E = 0 # Angle -- 180
                self.R = 0 # Angle -- 270
                self.Z = 0 # Increase Servo Angle
                self.C = 0 # Decrease Servo Angle
                
                ## For Oritentation (left and right or Forward)
                self.left = 0 # Turning Left                
                self.right = 0 # Turning Right

                ## For Thrust Control
                self.up = 0 # More Thrust
                self.down = 0 # Less Thrust
                
                ## For Device Control
                self.esc = 0 # Stop
                self.enter = 0 # Start 

                print("Socket Client Initialization is Successful!\r\n")

        except:
            print("UDP Initialization Failed! Please check your ip and port!\r\n")


    def scan_key(self):
        if self.server_or == 1:
            if keyboard.is_pressed('q'):
                self.Q = 1
            if keyboard.is_pressed('w'):
                self.W = 1
            if keyboard.is_pressed('e'):
                self.E = 1
            if keyboard.is_pressed('r'):
                self.R = 1
            if keyboard.is_pressed('z'):
                self.Z = 1
            if keyboard.is_pressed('c'):
                self.C = 1

            if keyboard.is_pressed('left'):
                self.left = 1
            if keyboard.is_pressed('right'):
                self.right = 1
            if keyboard.is_pressed('up'):
                self.up = 1
            if keyboard.is_pressed('down'):
                self.down = 1

            if keyboard.is_pressed('esc'):
                self.esc = 1
            if keyboard.is_pressed('enter'):
                self.enter = 1

        elif self.server_or == 0:
            print("Sorry, this is Client! Please Check!\r\n")


    def encode_to_str(self):
        send_string = str('')
        for value in self.Q,self.W,self.E,self.R,self.Z,self.C,self.left,self.right,self.up,self.right,self.esc,self.enter:
            send_string = send_string + str(value) + ','

        return send_string
    
    def decode_to_key(self):
        
        return 


