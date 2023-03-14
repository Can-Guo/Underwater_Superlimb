'''
Date: 2023-03-14 12:54:08
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-14 12:55:35
FilePath: /script/test_time.py
'''

from datetime import datetime
import time 

if __name__ == '__main__':
    
    
    print("Begin!\r\n")
    time.sleep(1)
    time_1 = datetime.now() 
    
    print(time_1)
    
    time.sleep(2)

    print(datetime.now())

    time.sleep(3)

    print(datetime.now())

    time.sleep(4)

    print(datetime.now())

    time.sleep(5)

    print(datetime.now())
