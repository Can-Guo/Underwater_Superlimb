'''
Date: 2022-08-13 11:14:48
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-13 11:19:55
FilePath: /python/test_method.py
'''
import numpy as np 

angle_list = np.zeros([10,3])

for i in range(10):
    angle_list[i,0]= i + 1

print(angle_list)

angle_list[:-1] = angle_list [1:]
print(angle_list)

angle_list[-1] = [22,23,14]
print(angle_list)
