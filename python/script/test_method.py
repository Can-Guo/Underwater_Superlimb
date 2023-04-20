'''
Date: 2022-12-20 20:52:32
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-04-17 15:12:50
FilePath: /script/test_method.py
'''
# import csv 
# import numpy as np 

# r1 = np.array([1,2,3])
# r2 = np.array([1,3])
# r3 =np.array([1,5,0,9])

# def trans(L):
#     return list(map(list,zip(*L)))
    
# R1=r1.transpose()
# R2=r2.transpose()
# R3=r3.transpose()


# with open("./test1.csv",'w') as csvfile:
#     writer = csv.writer(csvfile, lineterminator='\n')
#     writer.writerow(['c1', 'c2','c3'])
#     writer.writerows([R1,R2,R3])

# import pandas as pd 
# import numpy as np 
# a = [1,3,44]
# b = [1,2,3,4]

# # 不等维度数组合并
# df = pd.DataFrame({})
# for i in range(3):
#     df.insert(loc = i, column = 'do_{}'.format(i), value = a)

# df2 = pd.DataFrame({'do_3':b})
# df = pd.concat([df,df2], axis=1)

# # 保存为CSV文件
# df.to_csv("test_pd.csv", index=False, sep=',')

# # 读取CSV文件数据表头
# head_row = pd.read_csv("./test_pd.csv", nrows=0)
# head_row_list = list(head_row)
# # 读取具体数据
# csv_audio = pd.read_csv("./test_pd.csv", usecols=head_row_list)
# csv_audio_list = csv_audio.values.tolist()

# # 数组转置
# array = np.array(csv_audio_list)
# array = array.T

# # 删除NaN
# a1 = array[1]
# index = (~np.isnan(a1))

# print(a1[index])


import numpy as np 

a = np.array([[1,2,3,4],[4,5,6,7]])

sum = np.sum(a[0][-3:])
print(sum)