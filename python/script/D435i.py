'''
Date: 2022-07-27 22:43:23
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-08-13 17:08:21
FilePath: /python/script/D435i.py
'''

import pyrealsense2.pyrealsense2 as rs
import numpy as np
import math 

# import cv2


class D435i_Class(object):

    def __init__(self):

        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        self.config = rs.config()

        self.config.enable_stream(rs.stream.accel,rs.format.motion_xyz32f, 250)
        self.config.enable_stream(rs.stream.gyro, rs.format.motion_xyz32f, 200)

        # initialization of the Data List of IMU
        self.LENGTH = 10
        self.accel = np.zeros([self.LENGTH,3])
        self.gyro = np.zeros([self.LENGTH,3])

        # constant
        self.first = True
        self.alpha = 0.98
        


        # self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        # self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        # self.config.enable_stream(rs.stream.infrared, 1, 640, 480, rs.format.y8, 30)
        # self.config.enable_stream(rs.stream.infrared, 2, 640, 480, rs.format.y8, 30)


    def start_stream(self):
        # Start streaming
        self.pipeline.start(self.config)

    def gyro_data(self, gyro):
        return np.asarray([gyro.x, gyro.y, gyro.z])

    def accel_data(self, accel):
        return np.asarray([accel.x, accel.y, accel.z])

    def get_pipeline_frame(self):

        try:
            # while(True):
            for i in range(10):

                # Wait for a coherent pair of frames: depth and color
                frames = self.pipeline.wait_for_frames()

                # accel_frame = frames.get_accel_frame()
                # gyro_frame = frames.get_gyro_frame()

                accel_1_dim = self.accel_data(frames[0].as_motion_frame().get_motion_data())
                gyro_1_dim = self.gyro_data(frames[1].as_motion_frame().get_motion_data())


                # accel_2_dim = accel_1_dim.reshape([1,3])
                # self.accel = np.append(self.accel,accel_2_dim, axis=0)

                # gyro_2_dim = gyro_1_dim.reshape([1,3])
                # self.gyro = np.append(self.gyro, gyro_2_dim, axis = 0)

                self.accel = np.roll(self.accel, -3)
                self.gyro  = np.roll(self.gyro, -3)

                self.accel[self.LENGTH - 1,:] = accel_1_dim
                self.gyro[self.LENGTH - 1, :] = gyro_1_dim
       
                print("Accel List:\r\n ", self.accel)
                # print("Accel End :\r\n", self.accel[self.LENGTH-1,:])
                
                # print("Gyro List:\r\n ", self.gyro)
                # print("Accel End :\r\n", self.gyro[self.LENGTH-1,:])
                

                # depth_frame = frames.get_depth_frame()
                # color_frame = frames.get_color_frame()
                # ir_frame_left = frames.get_infrared_frame(1)
                # ir_frame_right = frames.get_infrared_frame(2)
                # if not depth_frame or not color_frame:
                #     continue

                # Convert images to numpy arrays
                # depth_image = np.asanyarray(depth_frame.get_data())
                # color_image = np.asanyarray(color_frame.get_data())
                # ir_left_image = np.asanyarray(ir_frame_left.get_data())
                # ir_right_image = np.asanyarray(ir_frame_right.get_data())

                # Apply colormap on depth image (image must be converted to 8-bit per pixel first)
                # depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

                # Stack both images horizontally
                # images1 = np.hstack((color_image, depth_colormap))
                # images2 = np.hstack((ir_left_image, ir_right_image))
                # Show images
                # cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
                # cv2.imshow('RealSense', images1)
                # cv2.imshow("Display pic_irt", images2)

                # key = cv2.waitKey(1)
                # Press esc or 'q' to close the image window
                # if key & 0xFF == ord('q') or key == 27:
                    # cv2.destroyAllWindows()
                    # break

        finally:
            # Stop streaming
            self.pipeline.stop()


    def get_IMU_update_Pose(self):
        
        frames = self.pipeline.wait_for_frames()

        accel = frames[0].as_motion_frame().get_motion_data()
        gyro = frames[1].as_motion_frame().get_motion_data()

        ts = frames.get_timestamp()

        global last_ts_gyro
        global accel_angle_x
        global accel_angle_y
        global accel_angle_z

        if self.first == True:
            self.first = False
            last_ts_gyro = ts

            accel_angle_z = math.degrees(math.atan2(accel.y, accel.z))
            accel_angle_x = math.degrees(math.atan2(accel.x, math.sqrt(accel.y**2 + accel.z**2)))
            accel_angle_y = math.degrees(math.degrees(math.pi))

        # calculate for the second frame onwards
        # gyro-meter calculations
        dt_gyro = (ts- last_ts_gyro) / 1000
        last_ts_gyro = ts

        # change in degree
        gyro_angle_x = gyro.x * dt_gyro # pitch
        gyro_angle_y = gyro.y * dt_gyro # yaw
        gyro_angle_z = gyro.z * dt_gyro # roll

        # angle in degree
        dangleX = gyro_angle_x * 180 / math.pi
        dangleY = gyro_angle_y * 180 / math.pi
        dangleZ = gyro_angle_z * 180 / math.pi

        total_gyro_angleX = accel_angle_x + dangleX
        total_gyro_angleY = accel_angle_y + dangleY
        total_gyro_angleZ = accel_angle_z + dangleZ

        # accelerometer calculation
        accel_angle_z = math.degrees(math.atan2(accel.y, accel.z))
        accel_angle_x = math.degrees(math.atan2(accel.x, math.sqrt(accel.y**2 + accel.z**2)))
        accel_angle_y = math.degrees(math.pi)

        # combining gyro-meter and accelerometer angles
        combined_angleX = total_gyro_angleX * self.alpha + accel_angle_x * (1-self.alpha)
        combined_angleZ = total_gyro_angleZ * self.alpha + accel_angle_z * (1-self.alpha)
        combined_angleY = total_gyro_angleY

        # consider the X-Y-Z coordinates, change the order of the axis to match the real situation
        print([accel.x, accel.y, accel.z, combined_angleZ, combined_angleY, combined_angleX])
        
        return([accel.x, accel.y, accel.z, combined_angleZ, combined_angleY, combined_angleX])


########################################################

D435i = D435i_Class()
D435i.start_stream()
# D435i.get_pipeline_frame()

# D435i.start_stream()
global last_ts_gyro;last_ts_gyro = 0.0
global accel_angle_x;accel_angle_x = 0
global accel_angle_y;accel_angle_y = 0
global accel_angle_z;accel_angle_z = 0

while True:
    D435i.get_IMU_update_Pose()

########################################################


