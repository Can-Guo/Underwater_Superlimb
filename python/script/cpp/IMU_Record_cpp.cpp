/*
 * @Date: 2023-01-12 11:45:16
 * @LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
 * @LastEditTime: 2023-03-10 17:40:44
 * @FilePath: /script/cpp/IMU_Record_cpp.cpp
 */


// for Microstrain IMU sensor using
#include "Microstrain_IMU_cpp.h"

// for time stamp generation
#include<ctime>
#include<sstream>
#include<iostream>

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

 // namespace declaration3.8
namespace fs = std::filesystem;
using namespace std;

// define pai for computation
#define Pai 3.1415926535

// Method 1: GET CURRENT TIMESTAMP for data collection

std::string GetCurrentTimeStamp()
{
    std::chrono::system_clock::time_point now = std::chrono::system_clock::now();
    std::time_t now_time_t = std::chrono::system_clock::to_time_t(now);
    std::tm* now_tm = std::localtime(&now_time_t);

    char buffer[40];
    strftime(buffer, sizeof(buffer), "%F %T", now_tm);

    std::ostringstream ss;
    ss.fill('0');

    std::chrono::milliseconds ms;

    ms = std::chrono::duration_cast<std::chrono::milliseconds> (now.time_since_epoch()) % 1000;
    ss << buffer << ":" << ms.count(); 
    string timestamp = ss.str();

    return string(timestamp);
    
}


// Method 2: Plot the imu data, record the data into CSV file at the same time

void Plot_Record_IMU_realtime(AHRS_IMU imu_class, string csv_file_name, bool plot_enable)
{
    // create a figure for plotting 
    if(plot_enable==true)
    {
        // plt::figure_size(1200,800);
    }

    // std::vector <double> accel_x, accel_y, accel_z, roll, pitch, yaw;

    // create a ofstream for CSV recording later
    ofstream fout(csv_file_name.c_str());

    // Step 1: write column name of the data into the first row of the CSV file
    fout << "Timestamp" << ',';
    for(int i=0; i<(imu_class.DataLabelName.size()-1); i++)
    {
        fout << imu_class.DataLabelName[i] << ',';
    }
    fout << imu_class.DataLabelName[imu_class.DataLabelName.size()-1] << endl;
    
    while (true)
    {
        // access one packet of the IMU data 
        string timestamp = GetCurrentTimeStamp();
        AHRS_IMU::ACCELERATION_EULER_ANGLE  accel_euler = imu_class.parseDataPacket_AHRS_IMU(500);
        // std::cout <<std::left<<setw(15) << "Acceleration " <<":" <<std::right<<setw(15)<< accel_euler.Acceleration.accel_x << " | " <<std::right<<setw(15)<< accel_euler.Acceleration.accel_y << " | " <<std::right<<setw(15)<<  accel_euler.Acceleration.accel_z << std::endl;
        // std::cout <<std::left<<setw(15) << "Euler Angle " <<":" <<std::right<<setw(15)<< accel_euler.Euler_Angle.roll << " | " <<std::right<<setw(15)<< accel_euler.Euler_Angle.pitch << " | " <<std::right<<setw(15)<< accel_euler.Euler_Angle.yaw << std::endl;

        // plot the imu data in one frame

        // accel_x.push_back(accel_euler.Acceleration.accel_x*9.8);
        // accel_y.push_back(accel_euler.Acceleration.accel_y*9.8);
        // accel_z.push_back(accel_euler.Acceleration.accel_z*9.8);

        // roll.push_back(accel_euler.Euler_Angle.roll/Pai*180.0);
        // pitch.push_back(accel_euler.Euler_Angle.pitch/Pai*180.0);
        // yaw.push_back(accel_euler.Euler_Angle.yaw/Pai*180.0);


        if(plot_enable==true)
        {
            // plt::clf();

            // plt::subplot(2,1,1);
            
            // plt::named_plot("Acceleration of X axis", accel_x,"r-");
            // plt::named_plot("Acceleration of Y axis", accel_y,"g-");
            // plt::named_plot("Acceleration of Z axis", accel_z,"b-");
            
            // plt::title("IMU Data Stream");
            // plt::xlabel("Time Sequence/frame");
            // plt::ylabel("Acceleration/g");
            // plt::legend();
            
            // plt::subplot(2,1,2);
            // plt::named_plot("Roll", roll,"r-.");
            // plt::named_plot("Pitch",  pitch,"g-.");
            // plt::named_plot("Yaw", yaw,"b-.");

            // plt::xlabel("Time Sequence");
            // plt::ylabel("Euler Angle / rad");
            // plt::legend();
            // plt::pause(0.001);
        }
        
        // write the raw data into CSV file 
        if(imu_class.DataLabelName[0] == "Acceleration_x")
        {
            fout  << timestamp << ","
                    << (accel_euler.Acceleration.accel_x)*9.8 << "," 
                    << (accel_euler.Acceleration.accel_y)*9.8 << ","
                    << (accel_euler.Acceleration.accel_z)*9.8 << ","
                    << (accel_euler.Euler_Angle.roll)/Pai*180.0 << ","
                    << (accel_euler.Euler_Angle.pitch)/Pai*180.0 << ","
                    << (accel_euler.Euler_Angle.yaw)/Pai*180.0 << endl;
        }

        // if: Acceleration Data Stream is after the Euler Angle Data Stream

        else if (imu_class.DataLabelName[0] == "roll")
        {
            fout  << timestamp << ","
                    << (accel_euler.Euler_Angle.roll)/Pai*180.0 << ","
                    << (accel_euler.Euler_Angle.pitch)/Pai*180.0 << ","
                    << (accel_euler.Euler_Angle.yaw)/Pai*180.0 << ","
                    << (accel_euler.Acceleration.accel_x)*9.8 << "," 
                    << (accel_euler.Acceleration.accel_y)*9.8 << ","
                    << (accel_euler.Acceleration.accel_z)*9.8 << endl;
        }
    }
}



// void Plot_IMU(AHRS_IMU imu_class, string csv_file_name)
// {

//     plt::figure_size(1200,800);
//     std::vector <double> accel_x, accel_y, accel_z, roll, pitch, yaw;

//     while (true)
//     {
//         // reading the CSV file recursive
//         // file path translation
//         std::cout << "RRRRR" << std::endl;

//         fs::path path_object = fs::current_path();
//         string CSV_file_name = string(fs::current_path().parent_path()) + "/csv_imu_0310/" + string(csv_file_name);

//         // read the data stream from CSV file, save into a vector
//         rapidcsv::Document doc(CSV_file_name, rapidcsv::LabelParams(0,-1));
//         vector <vector <float> > Data_Columns;

//         for(int i=0; i<imu_class.DataLabelName.size(); i++)
//         {
//             vector <float> column = doc.GetColumn<float>(imu_class.DataLabelName[i]);
//             Data_Columns.push_back(column);
//             // std::cout << "Column:%s" << column << std::endl;
//         }

//         int frame_number = Data_Columns[0].size();
        
//         accel_x.push_back(Data_Columns[0][frame_number-1]*9.8);
//         accel_y.push_back(Data_Columns[1][frame_number-1]*9.8);
//         accel_z.push_back(Data_Columns[2][frame_number-1]*9.8);

//         roll.push_back(Data_Columns[3][frame_number-1]/Pai*180.0);
//         pitch.push_back(Data_Columns[4][frame_number-1]/Pai*180.0);
//         yaw.push_back(Data_Columns[5][frame_number-1]/Pai*180.0);

//         plt::clf();

//         plt::subplot(2,1,1);
        
//         plt::named_plot("Acceleration of X axis", accel_x,"r-");
//         plt::named_plot("Acceleration of Y axis", accel_y,"g-");
//         plt::named_plot("Acceleration of Z axis", accel_z,"b-");
        
//         plt::title("IMU Data Stream");
//         plt::xlabel("Time Sequence/frame");
//         plt::ylabel("Acceleration/g");
//         plt::legend();
        
//         plt::subplot(2,1,2);
//         plt::named_plot("Roll", roll,"r-.");
//         plt::named_plot("Pitch",  pitch,"g-.");
//         plt::named_plot("Yaw", yaw,"b-.");

//         plt::xlabel("Time Sequence");
//         plt::ylabel("Euler Angle / rad");
//         plt::legend();
//         plt::pause(0.001);
//     }
// }

int main(int argc, char * argv[])
{
    // create an instance of the AHRS_IMU class
    AHRS_IMU imu_class;
    int SampleRate = 100;
    
    // configurate the data channel, activate channel field, enable data sampling
    imu_class.setDataChannel_Accel_IMU(SampleRate);
    imu_class.setDataChannel_Euler_Angles(SampleRate);
    imu_class.EnableDataStream_AHRS_IMU();

    string csv_file_name = imu_class.createCSV();
    
    // string time_stamp = GetCurrentTimeStamp();
    // std::cout << "Timestamp:\t" << time_stamp << std::endl;

    // Feature 1: plot IMU data,while record IMU data into CSV file at the same time

    bool plot_enable = false;
    // Plot_Record_IMU_realtime(imu_class, csv_file_name,  plot_enable);
    
    std::thread record_thread(Plot_Record_IMU_realtime,imu_class, csv_file_name,  plot_enable);
    record_thread.join();

    /////
    // Main procession
    // std::thread Plot_imu(Plot_IMU,imu_class,csv_file_name);
    // Plot_imu.join();

    // plt::figure_size(1200,800);
    // std::vector <double> accel_x, accel_y, accel_z, roll, pitch, yaw;

    // while (true)
    // {
    //     // reading the CSV file recursive
    //     // file path translation
    //     std::cout << "RRRRR" << std::endl;

    //     fs::path path_object = fs::current_path();
    //     string CSV_file_name = string(fs::current_path().parent_path()) + "/csv_imu_0310/" + string(csv_file_name);

    //     // read the data stream from CSV file, save into a vector
    //     rapidcsv::Document doc(CSV_file_name, rapidcsv::LabelParams(0,-1));
    //     vector <vector <float> > Data_Columns;

    //     for(int i=0; i<imu_class.DataLabelName.size(); i++)
    //     {
    //         vector <float> column = doc.GetColumn<float>(imu_class.DataLabelName[i]);
    //         Data_Columns.push_back(column);
    //         // std::cout << "Column:%s" << column << std::endl;
    //     }

    //     int frame_number = Data_Columns[0].size();
        
    //     accel_x.push_back(Data_Columns[0][frame_number-1]*9.8);
    //     accel_y.push_back(Data_Columns[1][frame_number-1]*9.8);
    //     accel_z.push_back(Data_Columns[2][frame_number-1]*9.8);

    //     roll.push_back(Data_Columns[3][frame_number-1]/Pai*180.0);
    //     pitch.push_back(Data_Columns[4][frame_number-1]/Pai*180.0);
    //     yaw.push_back(Data_Columns[5][frame_number-1]/Pai*180.0);

    //     plt::clf();

    //     plt::subplot(2,1,1);
        
    //     plt::named_plot("Acceleration of X axis", accel_x,"r-");
    //     plt::named_plot("Acceleration of Y axis", accel_y,"g-");
    //     plt::named_plot("Acceleration of Z axis", accel_z,"b-");
        
    //     plt::title("IMU Data Stream");
    //     plt::xlabel("Time Sequence/frame");
    //     plt::ylabel("Acceleration/g");
    //     plt::legend();
        
    //     plt::subplot(2,1,2);
    //     plt::named_plot("Roll", roll,"r-.");
    //     plt::named_plot("Pitch",  pitch,"g-.");
    //     plt::named_plot("Yaw", yaw,"b-.");

    //     plt::xlabel("Time Sequence");
    //     plt::ylabel("Euler Angle/rad");
    //     plt::legend();
        
    //     plt::pause(0.1);
    //     // plt::save("./image_imu_0310/1_111.png");
    //     // std::cout << "draw" <<std::endl;
    // }


    /////

    // Feature 2: plot imu data from CSV file
    // imu_class.plotDataCSV(string("Thu Jan 12 22:34:52 2023_imu_data.csv"),SampleRate);

}