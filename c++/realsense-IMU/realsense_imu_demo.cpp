/*
 * @Date: 2022-04-25 16:28:16
 * @LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
 * @LastEditTime: 2022-08-14 07:31:06
 * @FilePath: /realsense-IMU/realsense_imu_demo.cpp
 */

#include <librealsense2/rs.hpp>

#include <iostream>
#include <mutex>
#include <cstring>
#include <cmath>

// for record data into CSV
#include <fstream>
#include <string.h>
#include <stdio.h>
#include <vector>
#include <chrono>
#include <filesystem>
 
// for multi-thread 
#include <pthread.h>
#include <thread>

// for data plotting in realtime
#include "matplotlibcpp.h"
namespace plt = matplotlibcpp;

// for data reading from CSV file
#include "rapidcsv.h"

 // namespace declaration
namespace fs = std::filesystem ;
using namespace std;


#ifndef PI
const double PI = 3.14159265358979323846;
#endif


//////////////////////////////
// Basic Data Types         //
//////////////////////////////

struct float3 { 
    float x, y, z; 
    float3 operator*(float t)
    {
        return { x * t, y * t, z * t };
    }

    float3 operator-(float t)
    {
        return { x - t, y - t, z - t };
    }

    void operator*=(float t)
    {
        x = x * t;
        y = y * t;
        z = z * t;
    }

    void operator=(float3 other)
    {
        x = other.x;
        y = other.y;
        z = other.z;
    }

    void add(float t1, float t2, float t3)
    {
        x += t1;
        y += t2;
        z += t3;
    }
};


float3 Euler;
std::mutex Euler_mtx;

float3 Accel;
std::mutex Accel_mtx;


class Euler_Estimator
{

// private:

    // 补偿滤波器的权重参数--alpha
    float alpha = 0.98;
    bool first = true;

    double last_ts_gyro = 0;

    // 创建一个变量,用于保存陀螺仪y轴数据的初始值或offset.
    float gyro_y_initial = 0.0;


public:

    vector <string> DataLabelName = {"Acceleration of X axis", "Acceleration of Y axis", "Acceleration of Z axis", "roll", "pitch", "yaw" };

    void process_gyro(rs2_vector gyro_data, double ts)
    {
        // 对于第一次迭代,则将加速度数值作为相机的初始姿态
        if(first)
        {
            last_ts_gyro = ts;
            gyro_y_initial = gyro_data.y;
            return;
        }

        float3 gyro_angle;

        gyro_angle.x = gyro_data.x;                                     // pitch angle
        gyro_angle.y = gyro_data.y - gyro_y_initial;  // yaw angle
        gyro_angle.z = gyro_data.z;                                     // roll angle

        // 计算当前帧与上一帧的到达时刻之间的时间差
        double dt_gyro = (ts- last_ts_gyro) / 1000.0;
        last_ts_gyro = ts;

        // 过去一帧的角度变化量等于 ( 陀螺仪的数据 * 上述时间差 )
        gyro_angle = gyro_angle * dt_gyro;

        // 将得到的角度变化量应用于当前的欧拉角或姿态
        std::lock_guard <std::mutex> lock(Euler_mtx);
        // 根据坐标系的方向,累加于之前的姿态角或欧拉角
        
        Euler.add(gyro_angle.z, -gyro_angle.y,  gyro_angle.x);
        // Euler.add(-gyro_angle.z, -gyro_angle.y, gyro_angle.x);
        
    }


    void process_accel(rs2_vector accel_data)
    {
        // 声明变量,用于记录根据加速度换算得到的角度
        float3 accel_angle;

        // 更新并记录加速度的值
        // std::lock_guard <std::mutex> lock(Accel_mtx);
        Accel_mtx.lock();

        Accel.x = accel_data.x;
        Accel.y = accel_data.y;
        Accel.z = accel_data.z;

        // https://en.cppreference.com/w/cpp/thread/mutex/unlock
        Accel_mtx.unlock();

        // 根据加速度数据计算旋转角度Euler angle
        accel_angle.z = atan2(accel_data.y, accel_data.z);
        accel_angle.x = atan2(accel_data.x, sqrt(accel_data.y*accel_data.y + accel_data.z * accel_data.z));

        // 如果是第一次迭代,则根据加速度的数据作为相机的初始位姿
        std::lock_guard<std::mutex> lock(Euler_mtx);
        if(first)
        {
            first = false;
            Euler = accel_angle;
            // 由于我们无法根据加速度的数据来更新围绕y轴的角度,因此初始的Y轴角度设为一个常数值(根据坐标系的定义)
            Euler.y = PI;
        }
        else
        {
            // 应用补偿滤波器,更新姿态角或欧拉角
             /* 
            Apply Complementary Filter:
                - high-pass filter = theta * alpha:  allows short-duration signals to pass through while filtering out signals
                  that are steady over time, is used to cancel out drift.
                - low-pass filter = accel * (1- alpha): lets through long term changes, filtering out short term fluctuations 
            */
           Euler.x = Euler.x * alpha + accel_angle.x * (1-alpha);
           Euler.z = Euler.z * alpha + accel_angle.z * (1-alpha);
        }
    }


    // Returns the current Euler angle of rotation
    float3 get_euler()
    {
         std::lock_guard<std::mutex> lock(Euler_mtx);
        //  std::cout << " Theta: " << Euler.x << " | " << Euler.y << " | " << Euler.z << std::endl;
        return Euler;
    }

    // Returns the current Acceleration of the system
    float3 get_accel()
    {
         std::lock_guard<std::mutex> lock(Accel_mtx);
        //  std::cout << " Accel: " << Accel.x << " | " << Accel.y << " | " << Accel.x << std::endl;
        return Accel;
    }


    float3 to_deg(float3 angles_radian)
    {
        float3 Angles_deg;
        
        Angles_deg.x = angles_radian.x * 180.0 / PI;
        Angles_deg.y = angles_radian.y * 180.0 / PI;
        Angles_deg.z = angles_radian.z * 180.0 / PI;

        return Angles_deg;
    }


    string createCSV()
    {
        /*
        * Function : Create a CSV file for data stream sampling.
        * 
        * params : void
        * 
        * return : string (csv_filename)
        * 
        */

        auto now = chrono::system_clock::now();
        time_t tt;
        tt = chrono::system_clock::to_time_t (now);
        ostringstream oss;
        oss << ctime(&tt);
        string time = oss.str(); 

        // access the path to meet your personal system path.
        fs::path path_object = fs::current_path();
        string filename = string(path_object) + "/csv/" + string(time) + ".csv";

        ofstream fout(filename.c_str());
        fout.close();

        return string(filename);

    }


    bool check_imu_is_supported()
    {
        bool found_gyro = false;
        bool found_accel = false;
        rs2::context ctx;
        for (auto dev : ctx.query_devices())
        {
            // The same device should support gyro and accel
            found_gyro = false;
            found_accel = false;
            for (auto sensor : dev.query_sensors())
            {
                for (auto profile : sensor.get_stream_profiles())
                {
                    if (profile.stream_type() == RS2_STREAM_GYRO)
                        found_gyro = true;

                    if (profile.stream_type() == RS2_STREAM_ACCEL)
                        found_accel = true;
                }
            }
            if (found_gyro && found_accel)
                break;
        }
        return found_gyro && found_accel;
    }
    
};




string plot_data_CSV(Euler_Estimator Euler_class, string csv_file_name,  double executation_time)
{
    /*
    * Function : Plot data stream from CSV file.
    * 
    * params :  string (csv_file_name)
    *           double (executation_time)
    * 
    * return : string (figure_name)
    * 
    */

   rapidcsv::Document doc(csv_file_name, rapidcsv::LabelParams(0, -1));

   vector <vector  < float>>  Data_Columns;

   for(int i=0; i<Euler_class.DataLabelName.size() ; i++)
   {
       vector < float> column = doc.GetColumn<float>(Euler_class.DataLabelName[i]);
       Data_Columns.push_back(column);
   }

   // create the time frame sequence of the timestamp

   int frame_number = Data_Columns[0].size();
   vector <double> time_frame(frame_number);

    for(int n = 0; n < frame_number;  n++)
    {
        time_frame[n] = double(0.0 + n* (executation_time / frame_number));
    }

    plt::figure_size(1200, 780);
    
    for(int i =0; i< Euler_class.DataLabelName.size(); i++)
    {
        plt::named_plot(string(Euler_class.DataLabelName.at(i)), time_frame, Data_Columns.at(i));
    }

    // plt::xlim(0.0, executation_time);

    plt::title("Sample IMU Data Scream");
    plt::xlabel("Time Sequence");
    plt::ylabel("IMU Data");

    plt::legend();

    // access current time of the system, to create a file name for figure generated
    auto now = chrono::system_clock::now();
    time_t tt;
    tt = chrono::system_clock::to_time_t (now);
    ostringstream oss;
    oss << ctime(&tt);
    string time = oss.str(); 
    string fig_name = "./figure/" + string(time) + ".png";

    // access the parent path of the system
    fs::path path_object = fs::current_path();
    // std::cout << "Path: " << string(path_object.parent_path()) << endl;

    // std::cout << "\r\nSaving figure of the current plot!" << endl;
    // save a png figure for the current plot
    plt::save(fig_name);
    plt::show();

    std::cout << "\r\nPlot the data stream is successful!";

    fig_name = string(path_object.parent_path()) + "./figure/" + string(time) + ".png";

    return fig_name;

}



string recordToCSV(Euler_Estimator Euler_class, int frame_number)
{
    // if(first_iteration)
    // {
    string csv_file_name = Euler_class.createCSV() ;
    std::cout << " File location : " << csv_file_name << std::endl;
    // first_iteration = false;
    // }
    
    ofstream fout(csv_file_name.c_str());
    
    // Step 1: write column name of the data into the first row of the CSV file
    for(int i=0; i<(Euler_class.DataLabelName.size()-1); i++)
    {
        fout << Euler_class.DataLabelName[i] << ',';
    }
    fout << Euler_class.DataLabelName[Euler_class.DataLabelName.size()-1] << endl;

    // Step 2: access one frame of the data inside the for loop, and write into CSV file in one row.

    for(int n=0; n < frame_number; n++)
    {
        // access the data by pipeline
        float3 Euler_angle = Euler_class.to_deg(Euler_class.get_euler());
        float3 Acceleration = Euler_class.get_accel();

        std::cout << "Data for CSV: " << Acceleration.x << " | " <<  Acceleration.y << " | " << Acceleration.z << " | " << Euler_angle.x << " | " << Euler_angle.y <<  " | " << Euler_angle.z << std::endl;

        fout << Acceleration.x << "," << Acceleration.y << "," << Acceleration.z  << "," <<  Euler_angle.x << "," <<  Euler_angle.y << "," <<  Euler_angle.z << endl;

    }

    cout << "\r\nData Stream Recording is successful!\r\nPlease check CSV file at : " << csv_file_name << endl;
    fout.close();

    string fig_name = plot_data_CSV(Euler_class, csv_file_name, frame_number);

    std::cout << "\r\nGenerated Figure located at : " << fig_name  << endl;

    return csv_file_name;

}



void plot_data_dynamical(Euler_Estimator Euler_class, bool first_iteration, int frame_number)
{
    std::vector <double> accel_x, accel_y, accel_z, roll, pitch, yaw;

    // if(first_iteration)
    // {
    //     std::cout << " File location : " << Euler_class.createCSV() << std::endl;
    //     first_iteration = false;
    // }

    // vector<double> time_frame(frame_number);
    // double executation_time = frame_number / 1.0;
    // for(int n=0; n < frame_number; n++)
    // {
    //     time_frame[n] = double( 0.0 + n * (executation_time/frame_number));
    // }

    plt::figure_size(1200, 700);

    for(int i=0; i< frame_number; i++)
    {
        // access the data by pipeline
        float3 Euler_angle = Euler_class.to_deg(Euler_class.get_euler());
        float3 Acceleration = Euler_class.get_accel();

        accel_x.push_back(Acceleration.x);
        accel_y.push_back(Acceleration.y);
        accel_z.push_back(Acceleration.z);

        roll.push_back(Euler_angle.x);
        pitch.push_back(Euler_angle.y);
        yaw.push_back(Euler_angle.z);

        // if(i % 2 == 0)
        // {
        plt::clf();

        plt::subplot(2, 1, 1);
        plt::named_plot("Acceleration of X axis", accel_x);
        plt::named_plot("Acceleration of Y axis", accel_y);
        plt::named_plot("Acceleration of Z axis", accel_z);

        plt::title("IMU Data Scream");
        plt::xlabel("Time Sequence");
        plt::ylabel("Acceleration (m/s^2)");
        plt::legend();
        
        plt::subplot(2, 1, 2);
        plt::named_plot("Roll", roll);
        plt::named_plot("Pitch",  pitch);
        plt::named_plot("Yaw", yaw);

        // plt::plot(roll);
        // plt::plot(pitch);
        // plt::plot(yaw);


        // plt::title("IMU Data Scream");
        plt::xlabel("Time Sequence");
        plt::ylabel("Euler Angle / deg");
        plt::legend();

        plt::pause(0.0001);

        // }
    }
}



int main(int argc, char * argv[]) try
{

    Euler_Estimator Euler_class;

    // 1. 创建一个Euler_Estimator对象的实例,并且检查相机是否支持imu的配置

    if (!Euler_class.check_imu_is_supported())
    {
        std::cerr << "Device supporting IMU (D435i) not found";
        return EXIT_FAILURE;
    }
    else
        std::cout << "\r\nCongraduation! Device Supporting IMU (D435i) found! " << std::endl;

    // 2. 配置realsense数据流

    // 2.1 声明Realsense Pipeline
    rs2::pipeline pipe;
    // 2.2 为Pipeline创建一个config对象
    rs2::config config;
    // 2.3 添加加速度和陀螺仪的数据流到config配置对象中
    config.enable_stream(RS2_STREAM_ACCEL, RS2_FORMAT_MOTION_XYZ32F,250);
    config.enable_stream(RS2_STREAM_GYRO, RS2_FORMAT_MOTION_XYZ32F,200);


    // 3. 开始以给定的配置来获取数据流
    auto profile = pipe.start(config, [&] (rs2::frame frame)
    {
        // Cast the frame that arrived to motion frame
        auto motion = frame.as<rs2::motion_frame>();

        // If casting succeeded and the arrived frame is from gyro stream
        if (motion && motion.get_profile().stream_type() == RS2_STREAM_GYRO && motion.get_profile().format() == RS2_FORMAT_MOTION_XYZ32F)
        {
            // Get the timestamp of the current frame
            double ts = motion.get_timestamp();
            // Get gyro measures
            rs2_vector gyro_data = motion.get_motion_data();

            // std::cout<< "Gyro data in rs2_vector type:" << gyro_data.x << " | " <<   gyro_data.y << " | " <<  gyro_data.z << " | " <<  std::endl;

            // Call function that computes the angle of motion based on the retrieved measures
            Euler_class.process_gyro(gyro_data, ts);
        }
        // If casting succeeded and the arrived frame is from accelerometer stream
        if (motion && motion.get_profile().stream_type() == RS2_STREAM_ACCEL && motion.get_profile().format() == RS2_FORMAT_MOTION_XYZ32F)
        {
            // Get accelerometer measures
            rs2_vector accel_data = motion.get_motion_data();

            // std::cout << "Accel data in rs2_vector type:" << accel_data.x << " | " <<  accel_data.y << " | " <<  accel_data.z << " | " <<  std::endl;
            // Call function that computes the angle of motion based on the retrieved measures
            Euler_class.process_accel(accel_data);
        }
    });


    bool first_iteration = true;

    // for keyboard interruption
    // (void) pthread_create(&tld, 0, userInput_thread, 0);
    // (void) pthread_join(tld, NULL);


    // Method 1: print out the data with while loop 

    // while(true)
    // {
    //     if(first_iteration)
    //     {
    //         std::cout << " File location : " << Euler_class.createCSV() << std::endl;
    //         first_iteration = false;
    //     }
        
    //     float3 Euler_angle = Euler_class.to_deg(Euler_class.get_euler());
    //     float3 Acceleration = Euler_class.get_accel();

    //     // uncomment the following two lines if you want to see the data scream of Acceleration and Euler angles
    //     std::cout << "Euler (degree): " <<  std::right<<std::setw(8) << Euler_angle.x << " | " << std::right<<std::setw(8) << Euler_angle.y << " | " << std::right<<std::setw(8) << Euler_angle.z  << std::endl;
    //     std::cout << "Accel (m/s^2) : " <<  std::right<<std::setw(8) << Acceleration.x << " | " << std::right<<std::setw(8) << Acceleration.y << " | " << std::right<<std::setw(8) << Acceleration.z  << std::endl;

    // }

    //  Method 2: plot the data with matplotlib in realtime
    std::thread plot_thread(plot_data_dynamical, Euler_class, first_iteration, 10000);
    plot_thread.join();


    // Method 3:  record and plotting from CSV file
    // 4. 数据流保存至csv文件
    // 5. 绘图并且保存为png图片
    // std::thread record_thread(recordToCSV, Euler_class, 10000);
    // record_thread.join();
    
    return 0;

}


catch(const rs2::error & e)
{
    std::cerr << "RealSense error calling " << e.get_failed_function() << "(" << e.get_failed_args() << "):\n    " << e.what() << std::endl;
    return EXIT_FAILURE;
}


catch(const std::exception& e)
{
    std::cerr << e.what() << std::endl;
    return EXIT_FAILURE;
}

