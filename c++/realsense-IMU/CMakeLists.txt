cmake_minimum_required(VERSION 3.1.0)

project(RealsenseIMU)

# for plotting with matplotlib
find_package (Python2 COMPONENTS Interpreter Development)
find_package(PythonLibs REQUIRED)


# 添加源文件
add_executable(realsense_imu realsense_imu_demo.cpp)

add_executable(reading_imu_data  reading_imu_data.cpp)

# add_executable(realsense_imu rs-motion.cpp ../example.hpp ../../common/res/d435.h ${LZ4_DIR}/lz4.c)

# 设置C++17 标准, because we need filesystem feature provided by C++ 17 standard.
# https://stackoverflow.com/questions/48312460/c17-filesystem-is-not-a-namespace-name
set_property(TARGET realsense_imu PROPERTY CXX_STANDARD 17)

# for multi thread
# https://stackoverflow.com/questions/34143265/undefined-reference-to-symbol-pthread-createglibc-2-2-5
SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")

# for plotting with matplotlib
include_directories(${PYTHON_INCLUDE_DIRS})
include_directories(/usr/include/)
include_directories(/usr/include/python2.7/)
include_directories(/usr/local/lib)


# for OPENGL libraries
set(OpenGL_GL_PREFERENCE LEGACY)
find_package(OpenGL REQUIRED)
# target_include_directories(realsense_imu PRIVATE ${Python2_INCLUDE_DIRS})

target_link_libraries(realsense_imu  glfw OpenGL::GL )
target_link_libraries(realsense_imu  ${PYTHON_LIBRARIES})

# 链接realsense2库文件
target_link_libraries(realsense_imu realsense2 )

# target_link_libraries(realsense_imu ${PYTHON_LIBRARIES})

target_link_libraries(reading_imu_data realsense2)
target_link_libraries(realsense_imu stdc++fs)
# include_directories(../ ../../common/res ${LZ4_DIR})
# set_target_properties (realsense_imu PROPERTIES FOLDER Examples)
# install(TARGETS realsense_imu RUNTIME DESTINATION ${CMAKE_INSTALL_BINDIR})


