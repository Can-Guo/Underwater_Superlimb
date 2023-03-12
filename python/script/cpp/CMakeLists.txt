cmake_minimum_required(VERSION 3.8)
project(IMU_Record VERSION 1.0.0)


include(CTest)
include(CPack)

SET(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -pthread")

find_package (Python COMPONENTS Interpreter Development)
## 03.10
# set(Python_ADDITIONAL_VERSION 2.7)
find_package(PythonLibs REQUIRED)

message("Python_Found:${Python2_FOUND}")
message("Python_Version:${Python2_VERSION}")
message("Python_Development_FOUND:${Python2_Development_FOUND}")
message("Python_LIBRAR:${Python2_LIBRARIES}")

add_executable(imu_record_exe ${PROJECT_SOURCE_DIR}/IMU_Record_cpp.cpp)
# add_executable(class_demo ${PROJECT_SOURCE_DIR}/cpp_mscl_class_demo.cpp)


# set(CPACK_PROJECT_NAME ${PROJECT_NAME})
# set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

set(PYTHON_INCLUDE_DIRS ${PYTHON_INCLUDE_DIRS} /home/guoyucan/.local/lib/python3.8/site-packages/numpy/core/include/)
# set(PYTHON_INCLUDE_DIRS ${PYTHON_INCLUDE_DIRS} /home/guoyucan/.local/lib/python3.10/site-packages/numpy/core/include/)
include_directories(/usr/share/c++-mscl/Boost/include/)
include_directories(/usr/share/c++-mscl/source/)

# https://cmake.org/cmake/help/v3.17/module/FindPython2.html#module:FindPython2
# https://stackoverflow.com/questions/26953039/undefined-python-references-in-c-using-cmake

include_directories(${PYTHON_INCLUDE_DIRS})
include_directories(/usr/include/)
include_directories(/usr/include/python2.7/)
include_directories(/usr/local/lib)

# include_directories(/home/guoyucan/miniconda3/bin/python3)
# include_directories(/home/guoyucan/miniconda3/bin/python)
# include_directories(/home/guoyucan/miniconda3/lib/python3.10/site-packages)

# https://stackoverflow.com/questions/8774593/cmake-link-to-external-library
# target_link_libraries(simple_demo /usr/share/c++-mscl/libmscl.so)
# https://stackoverflow.com/questions/1620918/cmake-and-libpthread
# target_link_libraries(simple_demo pthread)

target_link_libraries(imu_record_exe /usr/share/c++-mscl/libmscl.so)
# target_link_libraries(class_demo pthread)
target_link_libraries(imu_record_exe ${PYTHON_LIBRARIES})


include_directories(${PYTHON_INCLUDE_DIRS})
# https://github.com/lava/matplotlib-cpp/issues/282


# https://zh.cppreference.com/w/cpp/filesystem/path/parent_path
target_compile_features(imu_record_exe PUBLIC cxx_std_17)


include(CMakePrintHelpers)
# cmake_print_properties(imu_record_exe ${PYTHON_LIBRARIES})


cmake_print_properties(
    TARGETS imu_record_exe    
    PROPERTIES COMPILE_FEATURES
)

cmake_print_properties(
  TARGETS imu_record_exe
  PROPERTIES LINK_LIBRARIES
)
