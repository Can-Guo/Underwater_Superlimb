
### This is a research project in [BionicDL](https://bionicdl.ancorasir.com/) Lab leading by Prof. Chaoyang Song@SUSTech.

### XBOX Driver Install & Testing by C++


### Microstrain IMU Driver: 
Follow instruments to install the MSCL library for MicroStrain Product
https://github.com/LORD-MicroStrain/MSCL/blob/master/HowToUseMSCL.md?

Clone this repository for simple Example Code if you are interested:
```
git clone https://github.com/Can-Guo/mscl_demo.git
```

### T200 Thrusters Driver Hardware Package:
The product details can be found at the link [BlueRobotics T200](https://bluerobotics.com/store/thrusters/t100-t200-thrusters/t200-thruster-r2-rp/)
Q: How can we control the T200 Thruster by Raspberry Pi or other Single Board Computer?
A: PWM control by [pigpio](http://abyz.me.uk/rpi/pigpio/download.html) library because it is efficient and convenient.

Download and install the latest version of the pigpio library

```
wget https://github.com/joan2937/pigpio/archive/master.zip
unzip master.zip
cd pigpio-master
make
sudo make install
```

If the python part of the installation fails, it may be because you need the setup tools.
```
sudo apt install python-setuptools python3-setuptools
```

To start the pigpio daemon (Before you use the pigpio library, you need to start the daemon.):
```
sudo pigpiod
```

To stop the pigpio daemon:
```
sudo killall pigpiod
```

### Dynamixel SDK for XW540 servo

Firstly, you need to modify the device ID for each Dynamixel, because different Dynamixel servos should have different device ID to avoid communication errors for the identical device ID.
You can change the device ID by [DYNAMIXEL Wizard 2.0](https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_wizard2/)

Download the DYNAMIXEL SDK 2.0 library

1) Method 1: Git Command
```
git clone https://github.com/ROBOTIS-GIT/DynamixelSDK.git
```

2) Method 2: Direct Download:
- [DYNAMIXEL SDK 3.7.31.zip](https://codeload.github.com/ROBOTIS-GIT/DynamixelSDK/zip/refs/tags/3.7.31)

Building the DYNAMIXEL SDK library:

- Run setup.py by entering the following command on the command prompt:

```
$ cd ~/DynamixelSDK/python 
$ sudo python setup.py install
# or you would like to use python3:
$ sudo python3 setup.py install
```

Building and running the Sample Code:

```
$ python read_write.py
# or you have setup the SDK for your python3
$ python3 read_write.py
```
