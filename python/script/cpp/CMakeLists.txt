cmake_minimum_required(VERSION 3.0.0)
project(IMU_Record VERSION 1.0.0)


include(CTest)
include(CPack)


find_package (Python2 COMPONENTS Interpreter Development)
find_package(PythonLibs REQUIRED)

enable_testing()

add_executable(imu_record_exe ${PROJECT_SOURCE_DIR}/IMU_Record_cpp.cpp)
# add_executable(class_demo ${PROJECT_SOURCE_DIR}/cpp_mscl_class_demo.cpp)


set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
set(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)

set(PYTHON_INCLUDE_DIRS ${PYTHON_INCLUDE_DIRS} /home/guoyucan/.local/lib/python3.8/site-packages/numpy/core/include/)

include_directories(/usr/share/c++-mscl/Boost/include/)
include_directories(/usr/share/c++-mscl/source/)

# https://cmake.org/cmake/help/v3.17/module/FindPython2.html#module:FindPython2
# https://stackoverflow.com/questions/26953039/undefined-python-references-in-c-using-cmake
include_directories(${PYTHON_INCLUDE_DIRS})
include_directories(/usr/include/)
include_directories(/usr/include/python2.7/)


# https://stackoverflow.com/questions/8774593/cmake-link-to-external-library
# target_link_libraries(simple_demo /usr/share/c++-mscl/libmscl.so)
# https://stackoverflow.com/questions/1620918/cmake-and-libpthread
# target_link_libraries(simple_demo pthread)

target_link_libraries(imu_record_exe /usr/share/c++-mscl/libmscl.so)
# target_link_libraries(class_demo pthread)
target_link_libraries(imu_record_exe ${PYTHON_LIBRARIES})
# https://zh.cppreference.com/w/cpp/filesystem/path/parent_path
target_compile_features(imu_record_exe PUBLIC cxx_std_17)

