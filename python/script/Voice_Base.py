'''
Date: 2022-11-14 16:28:57
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-11-24 01:44:45
FilePath: /script/Voice_Base.py
'''

import wave 
import pyaudio 
from scipy.io import wavfile
import matplotlib.pyplot as plt 
import numpy as np 

# plt.rcParams['font.family'] = ['sans-serif']
# plt.rcParams['font.sans-serif'] = ['SimHei']
# plt.rcParams['axes.unicode_minus'] = False

class Voice_Base(object):
    
    def __init__(self, path=[]):
        self.pa = pyaudio.PyAudio()

        for i in range(self.pa.get_device_count()):
            if(self.pa.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')) > 0:
                print('Input Device ID', i, '-', self.pa.get_device_info_by_host_api_device_index(0,i).get('name'))
        self.path = path

    
    def audiorecorder(self, len=60, formater = pyaudio.paInt16, rate = 16000, frames_per_buffer=1024, channels=2):
        '''
        函数功能：使用麦克风进行录音操作
        Input Param:
            len:录制时间长度(秒)
            formater:格式
            rate:采样率
            frames_per_buffer:
            channels: 通道数
        Return:
            None
        '''
        
        stream = self.pa.open(format=formater, channels=channels, rate=rate, input=True, input_device_index=15,  frames_per_buffer=frames_per_buffer)
        print("Microphone is Recording……")
        frames = []

        for i in range(0, int(rate/frames_per_buffer * len)):
            data = stream.read(frames_per_buffer)
            frames.append(data)
        
        print("Stop Recording……")

        stream.stop_stream()
        stream.close()

        self.pa.terminate()

        wf = wave.open(self.path, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(self.pa.get_sample_size(formater))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()
    

    def audiowrite(self, data, fs, binary = True, channel = 1, path=[]):
        '''
        函数功能：语音信息写入到.wav文件
        Input Param:
            data: 语音信号数据
            fs:采样率(Hz)
            binary: 是否写成二进制文件(只有在写出二进制文件才能用audioplayer播放)
            channel: 通道数
            path: 文件路径,默认为self.path的路径
        Return:
            None
        '''
        
        if len(path) == 0:
            path = self.path
        if binary:
            wf = wave.open(path,'wb')
            wf.setframerate(fs)
            wf.setnchannels(channel)
            wf.setsampwidth(2)
            wf.writeframes(b''.join(data))
        else:
            wavfile.write(path,fs,data)
    

    def audioread(self, return_nbits=True, formater='sample'):
        '''
                函数功能:读取语音文件,返回语音数据data,采样率fs,数据位数bits
        Input Param:
            formater:获取数据的格式,为sample时,数据为float32的[-1,1],
                     否则为文件本身的数据格式指定formater为任意非sample字符串,则返回原始数据
        Return:
            data: 语音数据
            fs: 采样率
            bits: 数据位数
        '''
        if return_nbits == True:
            fs, data, bits = wavfile.read(self.path)
        else:
            fs, data = wavfile.read(self.path)

        if formater == 'sample':
            data = data/(2**(bits-1))
        if return_nbits:
            return data, fs, bits 
        else:
            return data, fs
    

    def soundplot(self, data=[], samplerate=16000, size=(14,5)):
        """
        函数功能:将语音数据/或读取语音数据并绘制成图
        Input Param:
            data: 语音数据
            samplerate: 采样率
            size: 绘图窗口大小
        Return:
            None
        """
        if len(data) == 0:
            data, fs, _= self.audioread()
        plt.figure(figsize=size)
        x = [i/ samplerate for i in range(len(data))]
        plt.plot(x,data)
        plt.xlim([0, len(data) / samplerate])
        plt.xlabel('time/sec')
        plt.show()


    def soundadd(self, data1, data2):
        """
        函数功能: 将两个语音信号序列相加,若长短不一,在短的序列后端补零
        Input Param: 
            data1: 语音数据序列1
            data2: 语音数据序列2
        Return: 

        """
        if len(data1) < len(data2):
            temp = np.zeros([len(data2)])
            for i in range(len(data1)):
                temp[i] += data1[i]
            return temp + data2 

        elif len(data1) > len(data2):
            temp = np.zeros([len(data1)])
            for i in range(len(data2)):
                temp[i] += data2[i]
            return temp + data1 
        else:
            return data1 + data2


    def SPL_calculate(self, data, fs, frameLen):
        """
        函数功能: 根据数学公式计算单个声压值 $ y=\sqrt( \sum_{i=1} ^ Nx^2(i) ) $
        Input Param:
            data: 输入数据
            fs: 采样率
            frameLen: 计算声压的时间长度(ms单位)
        Return:
            单个声压数值
        """
        l = len(data)
        M = frameLen * fs / 1000
        if not l == M:
            exit('输入信号长度与所定义帧长不等!请检查!')
        # 计算有效声压
        pp = 0
        for i in range(int(M)):
            pp += (data[i] * data[i])
        pa = np.sqrt(pp / M)
        p0 = 2e-5
        spl = 20 * np.log10(pa / p0)

        return spl
    
    
    def SPL(self, data, fs, framLen=100, isplot=True):
        """
        计算声压曲线    
        Input Param:
            data: 语音信号数据
            fs: 采样率
            frameLen: 计算声压的时间长度(ms单位)
            isplot: 是否绘图，默认是
        Return: 
            返回声压列表spls
        """

        length = len(data)
        M = fs * framLen // 1000
        m = length % M 
        
        if not m < M // 2:
            # 最后一帧长度不小于M的一半
            data = np.hstack((data, np.zeros(M - m)))
        else:
            # 最后一帧长度小于M的一半
            data = data[:M * (length // M)]
        
        spls = np.zeros(len(data) // M)

        for i in range(len(data) // M - 1):
            s = data[i * M : (i+1) * M]
            spls[i] = self.SPL_calculate(s, fs, framLen)
        
        if isplot:
            plt.subplot(211)
            plt.plot(data)
            plt.subplot(212)
            plt.step([i for i in range(len(spls))], spls)
            plt.show()
        
        return spls 
    

    def enframe(self, x, win, inc=None):
        
        nx = len(x)
        
        if isinstance(win, list) or isinstance(win, np.ndarray):
            nwin = len(win)
            nlen = nwin  # 帧长=窗长
        
        elif isinstance(win, int):
            nwin = 1
            nlen = win  # 设置为帧长
        
        if inc is None:
            inc = nlen
        
        nf = (nx - nlen + inc) // inc
        frameout = np.zeros((nf, nlen))
        indf = np.multiply(inc, np.array([i for i in range(nf)]))
        
        for i in range(nf):
            frameout[i, :] = x[indf[i]:indf[i] + nlen]

        if isinstance(win, list) or isinstance(win, np.ndarray):
            frameout = np.multiply(frameout, np.array(win))
        return frameout

    # 矩形窗
    def reg_window(self, N):
        return np.ones(N)

    # 汉宁窗
    def hanning_window(self, N):
        nn = [i for i in range(N)]
        return 0.5 * (1 - np.cos(np.multiply(nn, 2 * np.pi) / (N - 1)))

    # 海明窗口
    def hamming_window(self, N):
        nn = [i for i in range(N)]
        return 0.54 - 0.46 * np.cos(np.multiply(nn, 2 * np.pi) / (N - 1))

    
    def STAc(self, x):
        """
        计算短时相关函数
        :param x:
        :return:
        """
        para = np.zeros(x.shape)
        fn = x.shape[1]
        for i in range(fn):
            R = np.correlate(x[:, i], x[:, i], 'valid')
            para[:, i] = R
        return para


    def STEn(self, x, win, inc):
        """
        计算短时能量函数
        :param x:
        :param win:
        :param inc:
        :return:
        """
        X = self.enframe(x, win, inc)
        s = np.multiply(X, X)
        return np.sum(s, axis=1)


    def STMn(self, x, win, inc):
        """
        计算短时平均幅度计算函数
        :param x:
        :param win:
        :param inc:
        :return:
        """
        X = self.enframe(x, win, inc)
        s = np.abs(X)
        return np.mean(s, axis=1)


    def STZcr(self, x, win, inc, delta=0):
        """
        计算短时过零率
        :param x:
        :param win:
        :param inc:
        :return:
        """
        absx = np.abs(x)
        x = np.where(absx < delta, 0, x)
        X = self.enframe(x, win, inc)
        X1 = X[:, :-1]
        X2 = X[:, 1:]
        s = np.multiply(X1, X2)
        sgn = np.where(s < 0, 1, 0)
        return np.sum(sgn, axis=1)


    def STAmdf(self, X):
        """
        计算短时幅度差，好像有点问题
        :param X:
        :return:
        """
        # para = np.zeros(X.shape)
        fn = X.shape[1]
        wlen = X.shape[0]
        para = np.zeros((wlen, wlen))
        for i in range(fn):
            u = X[:, i]
            for k in range(wlen):
                en = len(u)
                para[k, :] = np.sum(np.abs(u[k:] - u[:en - k]))
        return para


    def FrameTimeC(self, frameNum, frameLen, inc, fs):
        ll = np.array([i for i in range(frameNum)])
        return ((ll - 1) * inc + frameLen / 2) / fs


    def findSegment(self, express):
        """
        分割成语音片段
        :param express:
        :return:
        """
        if express[0] == 0:
            voiceIndex = np.where(express)
        else:
            voiceIndex = express
        d_voice = np.where(np.diff(voiceIndex) > 1)[0]
        voiceseg = {}
        if len(d_voice) > 0:
            for i in range(len(d_voice) + 1):
                seg = {}
                if i == 0:
                    st = voiceIndex[0]
                    en = voiceIndex[d_voice[i]]
                elif i == len(d_voice):
                    st = voiceIndex[d_voice[i - 1]+1]
                    en = voiceIndex[-1]
                else:
                    st = voiceIndex[d_voice[i - 1]+1]
                    en = voiceIndex[d_voice[i]]
                seg['start'] = st
                seg['end'] = en
                seg['duration'] = en - st + 1
                voiceseg[i] = seg
        return voiceseg


    def vad_TwoThr(self, x, wlen, inc, NIS):
        """
        使用双门限法检测语音段
        :param x: 语音信号
        :param wlen: 分帧长度
        :param inc: 帧移
        :param NIS:
        :return:
        """
        maxsilence = 15
        minlen = 5
        status = 0
        y = self.enframe(x, wlen, inc)
        fn = y.shape[0]
        # 计算短时能量
        amp = self.STEn(x, wlen, inc)
        # 计算短时过零率
        zcr = self.STZcr(x, wlen, inc, delta=0.01)
        ampth = np.mean(amp[:NIS])
        zcrth = np.mean(zcr[:NIS])
        amp2 = 2 * ampth
        amp1 = 4 * ampth
        zcr2 = 2 * zcrth
        xn = 0
        count = np.zeros(fn)
        silence = np.zeros(fn)
        x1 = np.zeros(fn)
        x2 = np.zeros(fn)
        for n in range(fn):
            if status == 0 or status == 1:
                if amp[n] > amp1:
                    x1[xn] = max(1, n - count[xn] - 1)
                    status = 2
                    silence[xn] = 0
                    count[xn] += 1
                elif amp[n] > amp2 or zcr[n] > zcr2:
                    status = 1
                    count[xn] += 1
                else:
                    status = 0
                    count[xn] = 0
                    x1[xn] = 0
                    x2[xn] = 0

            elif status == 2:
                if amp[n] > amp2 and zcr[n] > zcr2:
                    count[xn] += 1
                else:
                    silence[xn] += 1
                    if silence[xn] < maxsilence:
                        count[xn] += 1
                    elif count[xn] < minlen:
                        status = 0
                        silence[xn] = 0
                        count[xn] = 0
                    else:
                        status = 3
                        x2[xn] = x1[xn] + count[xn]
            elif status == 3:
                status = 0
                xn += 1
                count[xn] = 0
                silence[xn] = 0
                x1[xn] = 0
                x2[xn] = 0
        el = len(x1[:xn])
        if x1[el - 1] == 0:
            el -= 1
        if x2[el - 1] == 0:
            print('Error: Not find endding point!\n')
            x2[el] = fn
        SF = np.zeros(fn)
        NF = np.ones(fn)
        for i in range(el):
            SF[int(x1[i]):int(x2[i])] = 1
            NF[int(x1[i]):int(x2[i])] = 0
        voiceseg = self.findSegment(np.where(SF == 1)[0])
        vsl = len(voiceseg.keys())
        return voiceseg, vsl, SF, NF, amp, zcr


##############################
# Test the Class Methods
AU = Voice_Base(path='./wav/test_2.8_help.wav')

####
## 功能 1: Record Audio
# AU.audiorecorder()

####

## 功能 2: Read Audio File, into data in list
data_two, fs, n_bits= AU.audioread()
# AU.soundplot()
data= data_two[:,1]   # 选择其中一个轨道的数据
# AU.SPL(data=data[:,1],fs=fs)


####
# 功能 3: 短时计算短时能量, 短时平均幅度,短时自相关
# inc = 100
# wlen = 200
# win = AU.hanning_window(wlen)
# N = len(data)
# time = [i / fs for i in range(N)]

# ## 短时能量
# EN = AU.STEn(data, win, inc) 
# ## 短时平均幅度
# Mn = AU.STMn(data, win, inc)

# X = AU.enframe(data, win, inc)
# X = X.T
# ## 短时自相关
# Ac = AU.STAc(X)
# Ac = Ac.T
# Ac = Ac.flatten()


# fig = plt.figure(figsize=(16, 13))

# plt.subplot(3, 1, 1)
# plt.plot(time, data)
# plt.title('(a)Voice_Waveform')

# plt.subplot(3, 1, 2)
# frameTime = AU.FrameTimeC(len(EN), wlen, inc, fs)
# plt.plot(frameTime, Mn)
# plt.title('(b)Short_Time_Amplitude_Spectrum')

# plt.subplot(3, 1, 3)
# plt.plot(frameTime, EN)
# plt.title('(c)Short_Time_Energy_Spectrum')

# # 显示图片
# # plt.show()
# # 保存图片

# plt.savefig('images/wave_energy_corr_Help.png')
####


####
## 功能4: 语音端点检测
# data, fs, n_bits = AU.audioread()
data /= np.max(data)

N = len(data)
wlen = 200
inc = 80
IS = 0.1
overlap = wlen - inc 
NIS = int((IS* fs - wlen) // inc+1)
fn = (N- wlen ) // inc + 1

frameTime = AU.FrameTimeC(fn, wlen, inc, fs)
time = [i / fs for i in range(N)]

voiceseg, vsl, SF, NF, amp, zcr = AU.vad_TwoThr(data, wlen, inc, NIS)

fig2 = plt.figure(figsize=(20, 15))

plt.subplot(3, 1, 1) 
plt.plot(time, data)
plt.xlabel("Time(s)")
plt.ylabel("Amplitude")

plt.subplot(3, 1, 2)
plt.plot(frameTime, amp)
plt.xlabel("Time(s)")
plt.ylabel("Short Time Energy")

plt.subplot(3, 1, 3)
plt.plot(frameTime, zcr)
plt.xlabel("Time(s)")
plt.ylabel("Short Time Zero-Crossing")

for i in range(vsl):
    plt.subplot(3, 1, 1)
    plt.plot(frameTime[voiceseg[i]['start']], 0, 'ok')
    plt.plot(frameTime[voiceseg[i]['end']], 0, 'or')


    plt.subplot(3, 1, 2)
    plt.plot(frameTime, amp, 'b')
    plt.plot(frameTime[voiceseg[i]['start']], 0, 'ok')
    plt.plot(frameTime[voiceseg[i]['end']], 0, 'or')

    plt.subplot(3, 1, 3)
    plt.plot(frameTime, zcr, 'b')
    plt.plot(frameTime[voiceseg[i]['start']], 0, 'ok')
    plt.plot(frameTime[voiceseg[i]['end']], 0, 'or')

plt.show()

# plt.savefig('images/TwoThr.png')
# plt.close()
####

##############################    

