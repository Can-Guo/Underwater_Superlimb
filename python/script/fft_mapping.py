
# -*- coding: utf-8 -*-


import numpy as np 
from scipy.fftpack import fft 
import matplotlib.pyplot as plt 

Fs = 10000
f1 = 390 
f2 = 20000

t = np.linspace(0,1,Fs)
noise1 = np.random.random(10000) 
noise2 = np.random.normal(1,10,10000)

y = 2*np.sin(2*np.pi*f1*t) + 5*np.sin(2*np.pi *f2 *t) + noise2 

def FFT(Fs, data):
    L = len (data)                        # 信号长度
    N =int(np.power(2,np.ceil(np.log2(L))))    # 下一个最近二次幂
    FFT_y1 = np.abs(fft(data,N))/L*2      # N点FFT 变化,但处于信号长度
    Fre = np.arange(int(N/2))*Fs/N        # 频率坐标
    FFT_y1 = FFT_y1[range(int(N/2))]      # 取一半
    return Fre, FFT_y1

Fre, FFT_y1 = FFT(Fs,y)
plt.figure()
plt.plot(Fre, FFT_y1)
plt.grid()
plt.show()
