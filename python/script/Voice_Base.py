'''
Date: 2022-11-14 16:28:57
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-12-08 00:51:25
FilePath: /script/Voice_Base.py
'''

import wave 
import pyaudio 
from scipy.io import wavfile
import matplotlib.pyplot as plt 
import numpy as np 
import noisereduce as nr

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
        
        stream = self.pa.open(format=formater, channels=channels, rate=rate, input=True, input_device_index=7,  frames_per_buffer=frames_per_buffer)
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


    def vad_revr(self, dst1, T1, T2):
        """
        端点检测反向比较函数
        :param dst1:
        :param T1:
        :param T2:
        :return:
        """
        fn = len(dst1)
        maxsilence = 8
        minlen = 5
        status = 0
        count = np.zeros(fn)
        silence = np.zeros(fn)
        xn = 0
        x1 = np.zeros(fn)
        x2 = np.zeros(fn)
        for n in range(1, fn):
            if status == 0 or status == 1:
                if dst1[n] < T2:
                    x1[xn] = max(1, n - count[xn] - 1)
                    status = 2
                    silence[xn] = 0
                    count[xn] += 1
                elif dst1[n] < T1:
                    status = 1
                    count[xn] += 1
                else:
                    status = 0
                    count[xn] = 0
                    x1[xn] = 0
                    x2[xn] = 0
            if status == 2:
                if dst1[n] < T1:
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
            if status == 3:
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
        # voiceseg = self.findSegment(np.where(SF == 1)[0])
        start, end, duration = self.findSegment(np.where(SF == 1)[0])
        # vsl = len(voiceseg.keys())
        vsl = len(start)
        return start, end, duration, vsl, SF, NF


    def findSegment(self, express):
        """
        函数功能:分割成语音片段
        Input Param:
            express:
        Return:
            voiceseg -- 包含所有语音片段的起始点和结束点,持续时间等信息
        """
        if express[0] == 0:
            voiceIndex = np.where(express)
        else:
            voiceIndex = express
        d_voice = np.where(np.diff(voiceIndex) > 1)[0]
        # voiceseg = {}
        # index = 0  # index to label the voiceseg
        start = []
        end = []
        duration = []
        if len(d_voice) > 0:
            for i in range(len(d_voice) + 1):                
                # seg = {}
                if i == 0:
                    st = voiceIndex[0]
                    en = voiceIndex[d_voice[i]]
                elif i == len(d_voice):
                    st = voiceIndex[d_voice[i - 1]+1]
                    en = voiceIndex[-1]
                else:
                    st = voiceIndex[d_voice[i - 1]+1]
                    en = voiceIndex[d_voice[i]]
                # seg['start'] = st
                # seg['end'] = en
                # seg['duration'] = en - st + 1

                if (en-st+1) >= 25:
                    # voiceseg[index] = seg
                    # index = index + 1
                    start.append(st)
                    end.append(en)
                    duration.append(en-st+1)

        # return voiceseg
        print(start)
        print(end)
        print(duration)
        return start, end, duration

    def vad_specEN(self, data, wnd, inc, NIS, thr1, thr2, fs):
        # import matplotlib.pyplot as plt
        from scipy.signal import medfilt
        x = self.enframe(data, wnd, inc)
        X = np.abs(np.fft.fft(x, axis=1))
        if len(wnd) == 1:
            wlen = wnd
        else:
            wlen = len(wnd)
        df = fs / wlen
        fx1 = int(250 // df + 1)  # 250Hz位置
        fx2 = int(3500 // df + 1)  # 500Hz位置
        km = wlen // 8
        K = 0.5
        E = np.zeros((X.shape[0], wlen // 2))
        E[:, fx1 + 1:fx2 - 1] = X[:, fx1 + 1:fx2 - 1]
        E = np.multiply(E, E)
        Esum = np.sum(E, axis=1, keepdims=True)
        P1 = np.divide(E, Esum)
        E = np.where(P1 >= 0.9, 0, E)
        Eb0 = E[:, 0::4]
        Eb1 = E[:, 1::4]
        Eb2 = E[:, 2::4]
        Eb3 = E[:, 3::4]
        Eb = Eb0 + Eb1 + Eb2 + Eb3
        prob = np.divide(Eb + K, np.sum(Eb + K, axis=1, keepdims=True))
        Hb = -np.sum(np.multiply(prob, np.log10(prob + 1e-10)), axis=1)
        for i in range(10):
            Hb = medfilt(Hb, 5)
        Me = np.mean(Hb)
        eth = np.mean(Hb[:NIS])
        Det = eth - Me
        T1 = thr1 * Det + Me
        T2 = thr2 * Det + Me
        # voiceseg, vsl, SF, NF = self.vad_revr(Hb, T1, T2)
        start, end, duration, vsl, SF, NF = self.vad_revr(Hb, T1, T2)
        return start, end, duration, vsl, SF, NF, Hb


    def vad_TwoThr(self, x, wlen, inc, NIS):
        """
        函数功能:使用双门限法检测语音段
        Input Param:
            x: 语音信号
            wlen: 分帧长度
            inc: 帧移
            NIS:
        Return:

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
            print('Error: Not find ending point!\n')
            x2[el] = fn
        SF = np.zeros(fn)
        NF = np.ones(fn)
        for i in range(el):
            SF[int(x1[i]):int(x2[i])] = 1
            NF[int(x1[i]):int(x2[i])] = 0
        # voiceseg = self.findSegment(np.where(SF == 1)[0])
        start, end, duration = self.findSegment(np.where(SF == 1)[0])
        # vsl = len(voiceseg.keys())
        vsl = len(start)
        return start, end, duration, vsl, SF, NF, amp, zcr


    def noise_reduce(self, voice_data, noise_data=[], sample_rate=16000):
        """
        函数功能: 为输入的语音信号降噪   
        Input Param:
            voice_data --  声音数据, list
            noise_data -- 噪声数据, list(可选参数)
            sample_rate -- 声音或噪声数据的采样率,默认是16000样本/s
        Return:
            reduced_voice_data -- 返回的经过降噪且归一化的数据, list

        """

        if voice_data == []:
            print("Parameter Errors for Noice Reduction! Please Check your voice data!")
        elif voice_data != [] and noise_data == []:
            reduced_voice_data = nr.reduce_noise(y=voice_data, sr=sample_rate)
        elif voice_data != [] and noise_data != []:
            reduced_voice_data = nr.reduce_noise(y=voice_data, y_noise=noise_data, sr=sample_rate)
        else:
            print("Please check noise reduction parameters!\r\n")

        # print("Type", type(reduced_voice_data))
        reduced_voice_data /= np.max(reduced_voice_data) # 归一化数据尺度

        # for i in range(len(reduced_voice_data)):
        #     if np.abs(reduced_voice_data[i]) <= 0.015:
        #         reduced_voice_data[i] = 0.0

        return reduced_voice_data


##############################
# Test the Class Methods
AU = Voice_Base(path='./wav_word/test_3.1_forward.wav')

####
# # 功能 1: Record Audio
# AU.audiorecorder(len=60)

####

## 功能 2: Read Audio File, into data in list
data_two, fs, n_bits= AU.audioread()
# AU.soundplot()
data_one= data_two[:,1]   # 选择其中一个轨道的数据

# AU.SPL(data=data[:,1],fs=fs)

####
## 功能3: Noise Reduction
reduced_data = AU.noise_reduce(voice_data=data_one, sample_rate=16000)
# reduced_data /= np.max(reduced_data) # 归一化数据尺度
data_one /= np.max(data_one)  # 归一化数据尺度

# N = len(data_one)
# time = [i / fs for i in range(N)]

# fig = plt.figure(figsize=(16, 13))

# plt.subplot(2, 1, 1)
# plt.plot(time, data_one)
# plt.title('(a) Voice_Waveform')

# plt.subplot(2, 1, 2)
# plt.plot(time,reduced_data)
# plt.title('(b) Voice_Waveform_After_NoiceReduction')
# plt.show()

###
# 功能 4: 短时计算短时能量, 短时平均幅度,短时自相关
# inc = 100
# wlen = 200
# win = AU.hanning_window(wlen)
# N = len(reduced_data)
# time = [i / fs for i in range(N)]

# ## 短时能量
# EN = AU.STEn(reduced_data, win, inc) 
# ## 短时平均幅度
# Mn = AU.STMn(reduced_data, win, inc)

# X = AU.enframe(reduced_data, win, inc)
# X = X.T
# ## 短时自相关
# Ac = AU.STAc(X)
# Ac = Ac.T
# Ac = Ac.flatten()


# fig = plt.figure(figsize=(16, 13))

# plt.subplot(3, 1, 1)
# plt.plot(time, reduced_data)
# plt.title('(a)Voice_Waveform')

# plt.subplot(3, 1, 2)
# frameTime = AU.FrameTimeC(len(EN), wlen, inc, fs)
# plt.plot(frameTime, Mn)
# plt.title('(b)Short_Time_Amplitude_Spectrum')

# plt.subplot(3, 1, 3)
# plt.plot(frameTime, EN)
# plt.title('(c)Short_Time_Energy_Spectrum')

# # 显示图片
# plt.show()

# 保存图片
# plt.savefig('images/wave_energy_corr_Help.png')
####


####
## 功能4: 语音端点检测(双门限法)
# data, fs, n_bits = AU.audioread()
# data /= np.max(data)  # 归一化数据尺度

N = len(reduced_data)
wlen = 200
inc = 80
IS = 0.1
overlap = wlen - inc 
NIS = int((IS* fs - wlen) // inc+1)
fn = (N- wlen ) // inc + 1

frameTime = AU.FrameTimeC(fn, wlen, inc, fs)
time = [i / fs for i in range(N)]

Start, End, Duration, vsl, SF, NF, amp, zcr = AU.vad_TwoThr(reduced_data, wlen, inc, NIS)

Frame_zero = np.zeros(len(Start))
Frame_start = []
Frame_end  = []
for i in range(len(Start)):
    Frame_start.append(frameTime[Start[i]])
    Frame_end.append(frameTime[End[i]])

plt.figure(figsize=(20, 15))

plt.subplot(3, 1, 1) 
plt.plot(time, reduced_data)
plt.plot(Frame_start, Frame_zero, 'ok', )
plt.plot(Frame_end, Frame_zero, 'or')
plt.xlabel("Time(s)")
plt.ylabel("Amplitude")

plt.subplot(3, 1, 2)
plt.plot(frameTime, amp)
plt.plot(Frame_start, Frame_zero, 'ok', )
plt.plot(Frame_end, Frame_zero, 'or')
plt.xlabel("Time(s)")
plt.ylabel("Short Time Energy")

plt.subplot(3, 1, 3)
plt.plot(frameTime, zcr)
plt.plot(Frame_start, Frame_zero, 'ok', )
plt.plot(Frame_end, Frame_zero, 'or')
plt.xlabel("Time(s)")
plt.ylabel("Short Time Zero-Crossing")


print("VoiceSeg: \r\n ", Duration)


####
## 功能5: 语音端点检测(Spectral Entropy Method)
# data, fs, n_bits = AU.audioread()
# data /= np.max(data)  # 归一化数据尺度
# IS = 0.25
# wlen = 200
# inc = 80
# N = len(reduced_data)
# time = [i / fs for i in range(N)]
# wnd = np.hamming(wlen)
# overlap = wlen - inc
# NIS = int((IS * fs - wlen) // inc + 1)
# thr1 = 0.99
# thr2 = 0.98

# Start, End, Duration, vsl, SF, NF, Enm = AU.vad_specEN(reduced_data, wnd, inc, NIS, thr1, thr2, fs)

# fn = len(SF)
# frameTime = AU.FrameTimeC(fn, wlen, inc, fs)

# Frame_zero = np.zeros(len(Start))
# Frame_start = []
# Frame_end  = []

# for i in range(len(Start)):
#     Frame_start.append(frameTime[Start[i]])
#     Frame_end.append(frameTime[End[i]])

# plt.figure(figsize=(20, 15))

# plt.subplot(2, 1, 1)
# plt.plot(time, reduced_data)
# plt.plot(Frame_start, Frame_zero, 'ok', )
# plt.plot(Frame_end, Frame_zero, 'or')
# plt.legend(['signal','start','end'])

# plt.subplot(2, 1, 2)
# plt.plot(frameTime, Enm, 'g')
# plt.plot(Frame_start, Frame_zero, 'ok', )
# plt.plot(Frame_end, Frame_zero, 'or')
# plt.legend(['Spectral Entropy','start','end'])
# plt.xlabel('Time/s')
print("VSL:%d" % vsl)

plt.savefig('images/single_word_twoThre_1207/3.1_forward_left_single_word.png')
plt.show()
# plt.close()
####

##############################    

