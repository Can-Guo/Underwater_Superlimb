/*
 * @Date: 2022-04-27 22:23:42
 * @LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
 * @LastEditTime: 2022-05-09 15:57:50
 * @FilePath: /realsense-IMU/reading_imu_data.cpp
 */

#include <librealsense2/rs.hpp>
#include <iostream>


int main(int argc, char * argv[]) 
{
rs2::pipeline pipe;

rs2::config cfg;
cfg.enable_stream(RS2_STREAM_ACCEL,RS2_FORMAT_MOTION_XYZ32F,250);
cfg.enable_stream(RS2_STREAM_GYRO,RS2_FORMAT_MOTION_XYZ32F,200);

pipe.start(cfg);

while (true) // Application still alive?
{
    rs2::frameset frameset = pipe.wait_for_frames();

    // Find and retrieve IMU data
    if (rs2::motion_frame accel_frame = frameset.first_or_default(RS2_STREAM_ACCEL))
    {
        rs2_vector accel_sample = accel_frame.get_motion_data();
        std::cout << "Accel:" << accel_sample.x << " |  " << accel_sample.y << " | " << accel_sample.z << std::endl;
        //...
    }

    if (rs2::motion_frame gyro_frame = frameset.first_or_default(RS2_STREAM_GYRO))
    {
        rs2_vector gyro_sample = gyro_frame.get_motion_data();
        std::cout << "Gyro:" << gyro_sample.x << " | " << gyro_sample.y << " | " << gyro_sample.z << std::endl;
        //...
    }
}

}