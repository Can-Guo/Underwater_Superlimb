'''
Date: 2022-11-14 16:28:57
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-11-14 17:26:07
FilePath: \script\Voice_Base.py
'''
import wave 
import pyaudio 

class Voice_Base(object):
    
    def __init__(self, path):
        self.path = path

    
    def audioreorder(self, len=2, formater = pyaudio.paInt16, rate = 16000, frames_per_buffer=1024, channels=2):
        """
        【函数功能：使用麦克风进行录音操作】

        Input Param:
            len:录制时间长度(秒)
            formater:格式
            rate:采样率
            frames_per_buffer:
            channels: 通道数
        Return:
            None
        """
        pa = pyaudio.PyAudio()
        stream = pa.open(format=formater, channels=channels, rate=rate, input=True, frames_per_buffer=frames_per_buffer)
        print("Microphone is Recording……")
        frames = []

        for i in range(0, int(rate/frames_per_buffer * len)):
            data = stream.read(frames_per_buffer)
            frames.append(data)
        
        print("Stop Recording……")

        stream.stop_stream()
        stream.close()

        pa.terminate()

        wf = wave.open(self.path, "wb")
        wf.setnchannels(channels)
        wf.setsampwidth(pa.get_sample_size(formater))
        wf.setframerate(rate)
        wf.writeframes(b''.join(frames))
        wf.close()
    
    def audiowrite(self, data, fs, binary = True, channel = 1, path=[]):

        """
        【函数功能：语音信息写入到.wav文件】
        Input Param:
            data: 语音信号数据
            fs:采样率(Hz)
            binary: 是否写成二进制文件(只有在写出二进制文件才能用audioplayer播放)
            channel: 通道数
            path: 文件路径,默认为self.path的路径
        Return:
            None
        """

        if len(path) == 0:
            path = self.path
        if 