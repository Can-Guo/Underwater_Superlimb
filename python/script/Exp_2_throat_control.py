'''
Date: 2023-03-10 20:10:46
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-14 20:45:30
FilePath: /script/Exp_2_throat_control.py
'''


import socket as Socket
import time 


## socket TCP: ubuntu(server) <==> Raspberry Pi 4B
port = 3344
# ## socket TCP : Ubuntu(server) <==> Raspberry Pi 4B
s= Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
s.bind(("10.12.234.126",port))
s.listen(10)
client_socket,clienttAddr=s.accept()

## socket TCP : Ubuntu(client) <==> Mi-notebook (server)


import socket as Socket
socket_Mi = Socket.socket(Socket.AF_INET, Socket.SOCK_STREAM)
socket_Mi.settimeout(5000)
socket_Mi.connect(("10.13.228.137", 8888))


def encodeMI(data_mi):

    send_string = str(data_mi) + '!'

    print("Encoded Data: %s" % send_string)

    # pass 
    return send_string


if __name__ == '__main__':

    time.sleep(0.5)

    while(True):
        # print("Waiting!")

        try:
            data_Mi = socket_Mi.recv(1024)
        except BlockingIOError as e:
            print("Error when communicate with Notebook!")

        send_string = encodeMI(data_Mi.decode('utf-8'))
        print("To be send:", send_string)
        

        client_socket.send(send_string.encode('utf-8'))

        # time.sleep(0.05)

        # pass 
    
    

    
