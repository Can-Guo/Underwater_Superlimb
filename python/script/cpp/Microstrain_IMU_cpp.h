/*
 * @Date: 2023-01-12 11:33:13
 * @LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
 * @LastEditTime: 2023-03-10 01:48:44
 * @FilePath: /script/cpp/Microstrain_IMU_cpp.h
 */


#include <iostream>
#include <fstream>
#include <string.h>
#include <stdio.h>
#include <vector>
#include <chrono>
#include <filesystem>

// for time stamp generation
#include<ctime>
#include<sstream>
// #include <iostream>

#include "rapidcsv.h"
#include <cmath>
#include "mscl/mscl.h"

#include "matplotlibcpp.h"
namespace plt = matplotlibcpp;
namespace fs = std::filesystem ;

using namespace std;


class AHRS_IMU
{

private:

    mscl::Connection connection;
    mscl::MipChannels ahrsImuChs;

    bool SUCCESS;

    // data type for integration of data stream

    struct EULER_ANGLE{
        float roll;
        float pitch;
        float yaw;
    };

    struct ACCELERATION{
        float accel_x;
        float accel_y;
        float accel_z;
    };

public:

    struct ACCELERATION_EULER_ANGLE{
        ACCELERATION Acceleration;
        EULER_ANGLE Euler_Angle;

        // constructor of structure
        ACCELERATION_EULER_ANGLE()
        {
            Acceleration = {0.0, 0.0, 0.0}; 
            Euler_Angle = {0.0, 0.0, 0.0}; 
        }

        ACCELERATION_EULER_ANGLE(ACCELERATION Acceleration, EULER_ANGLE Euler_Angle)
        {
            Acceleration = Acceleration;
            Euler_Angle = Euler_Angle;
        }
    };

private: 

    /* data */
    ACCELERATION_EULER_ANGLE acceleration_euler_angle;
    /* data */

public:

    /* data */
    
    ACCELERATION_EULER_ANGLE accele_euler;
    vector <AHRS_IMU::ACCELERATION_EULER_ANGLE> acceleration_euler_list;
    vector <string> DataLabelName;

    //TODO:if you add other data stream, please modified this DataSelecter.
    enum DataSelecter {Null=0x00, Accel=0x01, Euler=0x10, Accel_and_Euler=0x11};
    enum DataSelecter dataSelecter = Null; 

    /* data */


public:

    AHRS_IMU();

    ~AHRS_IMU() {};

    void setToIdle();

    void resumeDataStream();

    void EnableDataStream_AHRS_IMU();

    void setDataChannel_Accel_IMU(int SampleRate);

    void setDataChannel_Euler_Angles(int SampleRate);

    AHRS_IMU::ACCELERATION_EULER_ANGLE parseDataPacket_AHRS_IMU(int Timeout_ms);

    //Method or feature for multi-packets Data access
    vector <AHRS_IMU::ACCELERATION_EULER_ANGLE> parseDataStream_AHRS_IMU(int Timeout_ms, int PacketNumber);

    //Method or feature for data recording
    string GetCurrentTimeStamp();
    string createCSV();
    string recordDataToCSV(vector <AHRS_IMU::ACCELERATION_EULER_ANGLE> acceleration_euler_angle);

    //TODO: Method to plot the data stream from CSV file generated before
    string plotDataCSV(string csv_file_name, int sample_rate);

};


AHRS_IMU::AHRS_IMU() //(/* args */)
{
    /*
    * Function : Constructor of the Class AHRS_IMU
    * 
    * params : void
    * 
    * return : void
    * 
    */
    
    // initialize the acceleration and euler angle data structure
    acceleration_euler_angle = {{0.0, 0.0, 0.0},{0.0, 0.0, 0.0}}; 

    // TODO: you need to define the USB port of the sensor device in your system
    const string USB_PORT = "/dev/ttyACM0";
    
    // create the connection object with port and baud rate
    AHRS_IMU::connection = mscl::Connection::Serial(USB_PORT);

    // create the InertialNode, passing in the connection
    mscl::InertialNode node(AHRS_IMU::connection);

    // create a MipChannel for configurate
    mscl::MipChannel ahrsImuChs;

    // ping the node
    AHRS_IMU::SUCCESS = node.ping();

    if(AHRS_IMU::SUCCESS == true)
    {   
        // print out information of the sensor device
        std::cout << "Node Information: " << endl;
        std::cout << "Model Name: " << node.modelName() << endl;
        std::cout << "Model Number: " << node.modelNumber() << endl;
        std::cout << "Serial: " << node.serialNumber() << endl;
        std::cout << "Firmware: " << node.firmwareVersion().str() << endl << endl;
    }

}


void AHRS_IMU::setToIdle()
{
    /*
    * Function : Set the sensor into Idle mode.
    * 
    * params : void
    * 
    * return : void
    * 
    */

    mscl::InertialNode node(AHRS_IMU::connection);
    node.setToIdle();
    std::cout << "Set the sensor to Idle state." << endl;
}


void AHRS_IMU::resumeDataStream()
{
    /*
    * Function : Resume to data stream before Idle mode.
    * 
    * params : void
    * 
    * return : void
    * 
    */

    mscl::InertialNode node(AHRS_IMU::connection);
    node.resume();
    std::cout << "Resume to data sampling." << endl;
}


void AHRS_IMU::EnableDataStream_AHRS_IMU()
{
    /*
    * Function : Enable data stream after you set the data channel of the channel field.
    * 
    * params : void
    * 
    * return : void
    * 
    */

    std::cout << "\r\nEnable Data Stream..." << endl;

    // create InertialNode, passing into the Connection
    mscl::InertialNode node(AHRS_IMU::connection);

    //set the active channels for the different data classes on the Node
    node.setActiveChannelFields(mscl::MipTypes::CLASS_AHRS_IMU, AHRS_IMU::ahrsImuChs);

    // start sampling the active channels on the AHRS/IMU class of the Node
    node.enableDataStream(mscl::MipTypes::CLASS_AHRS_IMU);

}


void AHRS_IMU::setDataChannel_Accel_IMU(int SampleRate)
{
    /*
    * Function :Configurate the channel of data stream to
    * include -> Acceleration.
    * 
    * params : (int) SampleRate (Hz)
    * 
    * return : void
    */

    if(AHRS_IMU::dataSelecter == 0x00)
    {
        AHRS_IMU::DataLabelName = {"Acceleration_x", "Acceleration_y", "Acceleration_z"};
        dataSelecter = Accel;
    }

    else if (AHRS_IMU::dataSelecter == 0x10)
    {
        AHRS_IMU::DataLabelName.push_back("Acceleration_x");
        AHRS_IMU::DataLabelName.push_back("Acceleration_y");
        AHRS_IMU::DataLabelName.push_back("Acceleration_z");
        dataSelecter = Accel_and_Euler;
    }

    AHRS_IMU::ahrsImuChs.push_back(mscl::MipChannel(mscl::MipTypes::CH_FIELD_SENSOR_SCALED_ACCEL_VEC, mscl::SampleRate::Hertz(SampleRate)));
    std::cout << "Added Acceleration Data Channel!\r\n" << endl;

}


void AHRS_IMU::setDataChannel_Euler_Angles(int SampleRate)
{

    /*
    * Function : Configurate the channel of data stream to
    * include -> Euler Angles
    * 
    * params : (int) SampleRate (Hz)
    * 
    * return : void
    * 
    */

    if(AHRS_IMU::dataSelecter == 0x00)
    {
        AHRS_IMU::DataLabelName = {"roll", "pitch", "yaw"};
        dataSelecter = Euler;
    }

    else if (AHRS_IMU::dataSelecter == 0x01)
    {
        AHRS_IMU::DataLabelName.push_back("roll");
        AHRS_IMU::DataLabelName.push_back("pitch");
        AHRS_IMU::DataLabelName.push_back("yaw");
        dataSelecter = Accel_and_Euler;
    }

    AHRS_IMU::ahrsImuChs.push_back(mscl::MipChannel(mscl::MipTypes::CH_FIELD_SENSOR_EULER_ANGLES, mscl::SampleRate::Hertz(SampleRate)));
    std::cout << "Added Euler Angles Data Channel!\r\n" << endl;

}


AHRS_IMU::ACCELERATION_EULER_ANGLE AHRS_IMU::parseDataPacket_AHRS_IMU(int Timeout_ms)
{
    /*
    * Function : Parse One Data Packet of {Acceleration,Euler_Angle}
    * 
    * params : (int) Timeout_ms (milliseconds)
    * 
    * return : (AHRS_IMU::ACCELERATION_EULER_ANGLE)
    * 
    */
    
    // std::cout << "\r\nParse One Data Packet ..." << endl;

    struct AHRS_IMU::EULER_ANGLE euler_angle = {0.0, 0.0, 0.0};
    struct AHRS_IMU::ACCELERATION acceleration ={0.0, 0.0, 0.0};

    mscl::InertialNode node(AHRS_IMU::connection);
    mscl::MipDataPackets packets = node.getDataPackets(Timeout_ms);

    for(mscl::MipDataPacket packet : packets)
    {
        packet.descriptorSet(); // the descriptor set of the packet

        // get all of the data points in the packet
        mscl::MipDataPoints points = packet.data();

        for(mscl::MipDataPoint dataPoint : points)
        {
            // Print out data to check or debug.
            // cout << "Data frame:" << right<<setw(15) << dataPoint.channelName() << " |"<<right<<setw(3) << dataPoint.storedAs()<<" | "<<right<<setw(15)<<dataPoint.as_float()<<endl;
            
            if (dataPoint.channelName() == string("roll"))
                euler_angle.roll  = dataPoint.as_float();
            if (dataPoint.channelName() == string("pitch"))
                euler_angle.pitch = dataPoint.as_float();
            if (dataPoint.channelName() == string("yaw"))
                euler_angle.yaw   = dataPoint.as_float();
            if (dataPoint.channelName() == string("scaledAccelX"))
                acceleration.accel_x = dataPoint.as_float();
            if (dataPoint.channelName() == string("scaledAccelY"))
                acceleration.accel_y = dataPoint.as_float();
            if (dataPoint.channelName() == string("scaledAccelZ"))
                acceleration.accel_z = dataPoint.as_float();
        }
    }

    acceleration_euler_angle.Acceleration = acceleration;
    acceleration_euler_angle.Euler_Angle = euler_angle;
    
    return acceleration_euler_angle;

}


// 

vector <AHRS_IMU::ACCELERATION_EULER_ANGLE>  AHRS_IMU::parseDataStream_AHRS_IMU(int Timeout_ms, int PacketNumber)
{
    /*
    * Function : Parse multiple packets for Acceleration and Euler Angle
    * 
    * params :  (int) Timeout_ms (milliseconds)
    *           (int) PacketNumber
    * 
    * return : vector <AHRS_IMU::ACCELERATION_EULER_ANGLE>
    * 
    */

    std::cout << "\r\nParse mutiple packets of the Data Stream ..." << endl;

    struct AHRS_IMU::ACCELERATION_EULER_ANGLE accel_euler_buffer;

    mscl::InertialNode node(AHRS_IMU::connection);
    

    for(int i=0; i<PacketNumber; i++)
    {
        mscl::MipDataPackets packets = node.getDataPackets(Timeout_ms, 1);

        for(mscl::MipDataPacket packet : packets)
        {
            // packet.descriptorSet(); // the descriptor set of the packet

            // get all of the points in the packet
            mscl::MipDataPoints data = packet.data();
            mscl::MipDataPoint dataPoint;

            for(unsigned int itr = 0; itr < data.size(); itr++)
            {
                dataPoint = data[itr];

                // Print out data to check or debug.
                // cout    << "Data frame:" << right<<setw(15) << dataPoint.channelName() << " |"<<right<<setw(3) 
                //         << dataPoint.storedAs()<<" | "<<right<<setw(15)<<dataPoint.as_float()<<endl;
                
                if (dataPoint.channelName() == string("roll"))
                    accel_euler_buffer.Euler_Angle.roll = dataPoint.as_float();
                if (dataPoint.channelName() == string("pitch"))
                    accel_euler_buffer.Euler_Angle.pitch = dataPoint.as_float();
                if (dataPoint.channelName() == string("yaw"))
                    accel_euler_buffer.Euler_Angle.yaw = dataPoint.as_float();
                if (dataPoint.channelName() == string("scaledAccelX"))
                    accel_euler_buffer.Acceleration.accel_x = dataPoint.as_float();
                if (dataPoint.channelName() == string("scaledAccelY"))
                    accel_euler_buffer.Acceleration.accel_y = dataPoint.as_float();
                if (dataPoint.channelName() == string("scaledAccelZ"))
                    accel_euler_buffer.Acceleration.accel_z = dataPoint.as_float();
            }

            // Print out the data stream to check or debugging.
            // cout    << "Data Before push_back : " 
            //         << accel_euler_buffer.Euler_Angle.roll << " | " << accel_euler_buffer.Euler_Angle.pitch << " | "
            //         << accel_euler_buffer.Euler_Angle.yaw << " | " << accel_euler_buffer.Acceleration.accel_x << " | "
            //         << accel_euler_buffer.Acceleration.accel_y << " | " << accel_euler_buffer.Acceleration.accel_z << endl;
                    
            acceleration_euler_list.push_back(accel_euler_buffer);

        }
    }
        
    return acceleration_euler_list;
}


string AHRS_IMU::GetCurrentTimeStamp()
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


string AHRS_IMU::createCSV()
{
    /*
    * Function : Create a CSV file for data stream sampling.
    * 
    * params : void
    * 
    * return : string (csv_filename)
    * 
    */

    // auto now = chrono::system_clock::now();
    // time_t tt;
    // tt = chrono::system_clock::to_time_t (now);
    // ostringstream oss;
    // oss << ctime(&tt);
    // string time = oss.str(); 


    // using GetCurrentTimeStamp() Method to access timestamp
    string time = AHRS_IMU::GetCurrentTimeStamp();

    // access the path to meet your personal system path.
    fs::path path_object = fs::current_path();
    string filename = string(path_object.parent_path().parent_path()) + "/csv_imu_0310/" + string(time.erase(time.size()-1)) + "_imu_data.csv";

    ofstream fout(filename.c_str());

    fout.close();
    std::cout << "CSV File Path:\t" << filename << std::endl;

    return string(filename);

}


string AHRS_IMU::recordDataToCSV(vector <AHRS_IMU::ACCELERATION_EULER_ANGLE> acceleration_euler_list)
{
    /*
    * Function : Record data stream into CSV file
    * 
    * params : vector <AHRS_IMU::ACCELERATION_EULER_ANGLE> 
    * 
    * return : string (csv_file_name)
    * 
    */

    // Step 0: open a CSV file
    string csv_file_name = AHRS_IMU::createCSV();
    ofstream fout(csv_file_name.c_str());

    // Step 1: write column name of the data into the first row of the CSV file
    for(int i=0; i<(AHRS_IMU::DataLabelName.size()-1); i++)
    {
        fout << DataLabelName[i] << ',';
    }
    fout << DataLabelName[AHRS_IMU::DataLabelName.size()-1] << endl;
    
    // Step 2: write all the data packets into CSV file, row by row
    for(int i=0; i< (AHRS_IMU::acceleration_euler_list.size()); i++)
    {
        if(AHRS_IMU::dataSelecter == 0x00 or AHRS_IMU::acceleration_euler_list.size() == 0)
        {
            std::cout << "No Data Packet Found! Please check!" << endl;
        }
        
        // if only enable the Acceleration Data Streaming
        else if (AHRS_IMU::dataSelecter == 0x01)
        {
            fout    << acceleration_euler_list[i].Acceleration.accel_x << "," 
                    << acceleration_euler_list[i].Acceleration.accel_y << ","
                    << acceleration_euler_list[i].Acceleration.accel_z << endl;
        }

        // if only enable the Euler Angle Data Streaming
        else if (AHRS_IMU::dataSelecter == 0x10)
        {
            fout    << acceleration_euler_list[i].Euler_Angle.roll << ","
                    << acceleration_euler_list[i].Euler_Angle.pitch << ","
                    << acceleration_euler_list[i].Euler_Angle.yaw << endl;
        }

        // if Enable Both of the Acceleration and Euler Angle 
        else if (AHRS_IMU::dataSelecter == 0x11)
        {

            // Print out the data to checking or debugging.
            // cout    <<left<<setw(15) << "Acceleration after push_back" <<":" <<right<<setw(15)
            //         << acceleration_euler_list[i].Acceleration.accel_x << " | " 
            //         <<right<<setw(15)<< acceleration_euler_list[i].Acceleration.accel_y << " | " 
            //         <<right<<setw(15)<< acceleration_euler_list[i].Acceleration.accel_z << endl;

            // cout    <<left<<setw(15) << "Euler Angle after push_back" <<":" <<right<<setw(15)
            //         << acceleration_euler_list[i].Euler_Angle.roll << " | " 
            //         <<right<<setw(15)<< acceleration_euler_list[i].Euler_Angle.pitch << " | " 
            //         <<right<<setw(15)<< acceleration_euler_list[i].Euler_Angle.yaw << endl;


            // Acceleration Data Stream is before the Euler Angle Data Stream

            if(AHRS_IMU::DataLabelName[0] == "Acceleration_x")
            {
                
                fout    << acceleration_euler_list[i].Acceleration.accel_x << "," 
                        << acceleration_euler_list[i].Acceleration.accel_y << ","
                        << acceleration_euler_list[i].Acceleration.accel_z << ","
                        << acceleration_euler_list[i].Euler_Angle.roll << ","
                        << acceleration_euler_list[i].Euler_Angle.pitch << ","
                        << acceleration_euler_list[i].Euler_Angle.yaw << endl;
            }

            // Acceleration Data Stream is after the Euler Angle Data Stream

            else if (AHRS_IMU::DataLabelName[0] == "roll")
            {
                fout    << acceleration_euler_list[i].Euler_Angle.roll << ","
                        << acceleration_euler_list[i].Euler_Angle.pitch << ","
                        << acceleration_euler_list[i].Euler_Angle.yaw << ","
                        << acceleration_euler_list[i].Acceleration.accel_x << "," 
                        << acceleration_euler_list[i].Acceleration.accel_y << ","
                        << acceleration_euler_list[i].Acceleration.accel_z << endl;
            }
        }

    }

    cout << "\r\nData Stream Recording is successful!\r\nPlease check CSV file at : " << csv_file_name << endl;

    fout.close();

    return csv_file_name;

}


string AHRS_IMU::plotDataCSV(string csv_file_name, int sample_rate)
{
    /*
    * Function : Plot data stream from CSV file.
    * 
    * params :  string (csv_file_name)
    *           int (sample_rate)
    * 
    * return : string (figure_name)
    * 
    */

   // file path translation
    fs::path path_object = fs::current_path();
    string CSV_file_name = string(fs::current_path().parent_path()) + "/csv_imu/" + string(csv_file_name);

    // read the data stream from CSV file, save into a vector
    rapidcsv::Document doc(CSV_file_name, rapidcsv::LabelParams(0,-1));
    vector <vector <float> > Data_Columns;

    // vector <string> DataLabelName = {"Acceleration_x", "Acceleration_y", "Acceleration_z", "roll", "pitch", "yaw"};

    for(int i=0; i<AHRS_IMU::DataLabelName.size(); i++)
    {
        vector <float> column = doc.GetColumn<float>(AHRS_IMU::DataLabelName[i]);
        Data_Columns.push_back(column);
    }

    // create the time frame sequence of the timestamp
    int frame_number = Data_Columns[0].size();
    vector<double> time_frame(frame_number);
    for(int n=0; n < frame_number; n++)
    {
        time_frame[n] = double( 0.0 + n * (frame_number/sample_rate));
    }

    float executation_time = (frame_number/sample_rate);

    // plot data with matplotplusplus libraries.
    plt::figure_size(1200, 800);

    for (int i = 0; i < AHRS_IMU::DataLabelName.size(); i++)
    {   
        plt::named_plot(string(AHRS_IMU::DataLabelName.at(i)), time_frame, Data_Columns.at(i)) ;
    }

    plt::xlim((int)(0), (int)(executation_time+1.0));
    plt::title("Sample Data Stream");
    plt::legend();
    

    // access current time of the system, to create a file name for figure generated
    auto now = chrono::system_clock::now();
    time_t tt;
    tt = chrono::system_clock::to_time_t (now);
    ostringstream oss;
    oss << ctime(&tt);
    string time = oss.str(); 
    string fig_name = "../image_imu/" + string(time.erase(time.size()-1)) + ".png";

    // access the parent path of the system
    // fs::path path_object = fs::current_path();
    // std::cout << "Path: " << string(path_object.parent_path()) << endl;

    // std::cout << "\r\nSaving figure of the current plot!" << endl;
    // save a png figure for the current plot
    plt::save(fig_name);
    plt::show();

    std::cout << "\r\nPlot the data stream from CSV file is successful!";

    fig_name = string(path_object.parent_path()) + "./image_imu/" + string(time) + ".png";

    return fig_name;

}


/*  #Testing demo for this Class deployment.
*  
*  Feature 1.  Parse one packet of data stream including {Acceleration,Euler_Angle}
*  
*  Feature 2.  Parse PacketNumber packets of data stream including {Acceleration,Euler_Angle}
* 
*  Feature 3.  Record data stream generated above into a CSV file
* 
*  Feature 4.  Plot the data stream recorded inside CSV file generated above,
*              and save into a png figure file.
*  
*/



// int main(int argc, char ** argv)
// {

//     // create an instance of the AHRS_IMU class.
//     AHRS_IMU imu;

//     int SampleRate = 250;
    
//     // TODO: Uncomment following two lines if you would like to change the Sample Rate by input number.
//     // std::cout << "Please change the Sampling Rate in (100-1000) Hz, default 500 Hz!" << endl;
//     // cin >> SampleRate;

//     // Configurate the data channel, activate channel field, enable data sampling.
//     imu.setDataChannel_Accel_IMU(SampleRate);
//     imu.setDataChannel_Euler_Angles(SampleRate);
//     imu.EnableDataStream_AHRS_IMU();


//     // Feature 1 : Parse one packet of data stream
//     imu.accele_euler = imu.parseDataPacket_AHRS_IMU(500);
//     std::cout <<std::left<<setw(15) << "Acceleration " <<":" <<std::right<<setw(15)<< imu.accele_euler.Acceleration.accel_x << " | " <<std::right<<setw(15)<< imu.accele_euler.Acceleration.accel_y << " | " <<std::right<<setw(15)<<  imu.accele_euler.Acceleration.accel_z << endl;
//     std::cout <<std::left<<setw(15) << "Euler Angle " <<":" <<std::right<<setw(15)<< imu.accele_euler.Euler_Angle.roll << " | " <<std::right<<setw(15)<< imu.accele_euler.Euler_Angle.pitch << " | " <<std::right<<setw(15)<< imu.accele_euler.Euler_Angle.yaw << endl;
    

//     // Feature 2 : Parse PacketNumber packets of data stream, you may change the PacketNumber to meet your needs.
    
//     // Start time of the executation of this part.
//     auto start = chrono::high_resolution_clock::now();

//     // TODO: you may need to change the packet number you would like to collect
//     int PacketNumber = 5000;
//     vector <AHRS_IMU::ACCELERATION_EULER_ANGLE> accel_euler_list = imu.parseDataStream_AHRS_IMU(500, PacketNumber);

//     // Elapsed time of the executation
//     auto elapsed = chrono::high_resolution_clock::now() - start;

//     std::cout << "\r\nParse data packets Executation Time is about " << chrono::duration_cast<chrono::microseconds> (elapsed).count()/1000.0 << " milliseconds." << endl;


//     // Feature 3 : Record data stream generated above into a CSV file
//     string file_name = imu.recordDataToCSV(accel_euler_list);
    
    
//     // Feature 4: Plot the data stream recorded inside CSV file generated above,
//     //            and save into a png figure.
//     string fig_name = imu.plotDataCSV(file_name, 1.0);

//     std::cout << "\r\nGenerated Figure located at : " << fig_name << endl << endl;

// }

// Testing demo end.
