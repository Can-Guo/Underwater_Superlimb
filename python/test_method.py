'''
Date: 2022-08-27 21:31:46
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-09-14 20:04:32
FilePath: \Underwater_Superlimb\python\test_method.py
'''
# '''
# Date: 2022-08-13 11:14:48
# LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
# LastEditTime: 2022-09-14 19:15:46
# FilePath: \Underwater_Superlimb\python\test_method.py
# '''



########################################
## 1. Test the create CSV file Method
# from datetime import datetime 
# import os 
# import csv 
# import platform 

# if platform.system().lower() == 'windows':
#     print("当前的操作系统是windows")
#     sys_platform = 'windows'
# elif platform.system().lower() == 'linux':
#     print("当前的操作系统是linux")
#     sys_platform = 'linux'

# print(sys_platform)

# def create_csv():
#     cwd = os.path.abspath('.')
#     dir = os.path.dirname(cwd)

#     time_mark = datetime.now()

#     time_mark = time_mark.strftime("%Y-%m-%d %H-%M-%S")
#     if sys_platform == 'windows':
#         file_name = str(dir) + '\csv\imu_data_' + str(time_mark) + '_save.csv'
#     elif sys_platform == 'linux':
#         file_name = str(dir) + '/csv/imu_data_' + str(time_mark) + '_save.csv'

#     # print(file_name)

#     with open(file_name, 'a') as file:
#         writer = csv.writer(file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
#         writer.writerow(['Timestamp', 'Accel_x', 'Accel_y', 'Accel_z', 'Roll', 'Pitch', 'Yaw'])

#     file.close()
            
# create_csv()
########################################


