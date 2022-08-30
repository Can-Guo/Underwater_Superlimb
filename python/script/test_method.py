'''
Date: 2022-08-30 21:58:32
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-30 22:15:46
FilePath: \script\test_method.py
'''


from datetime import datetime 
import os 
import csv 


def create_csv():
    cwd = os.path.abspath('.')
    dir = os.path.dirname(cwd)

    time_now = datetime.now()

    time_mark = time_now.strftime("%Y-%m-%d %H-%M-%S")
    file_name = str(dir) + '\csv\imu_data_' + str(time_mark) + '_save.csv'

    print(file_name)

    with open(file_name, 'a') as file:
        writer = csv.writer(file, delimiter = ',', quotechar = '"', quoting = csv.QUOTE_MINIMAL)
        writer.writerow(['Timestamp', 'Accel_x', 'Accel_y', 'Accel_z', 'Roll', 'Pitch', 'Yaw'])

    file.close()
            
create_csv()