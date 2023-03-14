'''
Date: 2023-03-13 10:34:38
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2023-03-13 11:08:55
FilePath: /script/Plot_Audio.py
'''

import os
import numpy as np 
import matplotlib.pyplot as plt 
import scienceplots 
plt.style.use(['science','no-latex'])

from scipy.io import wavfile


def audio_read(path=[],return_nbits=True,formater='sample'):
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

    if path == []:
        print("Please specific a Path to read WAV file!\r\n")

    else:
        if return_nbits == True:
            fs, data, bits = wavfile.read(path)
        else:
            fs, data = wavfile.read(path)
    
    if formater == 'sample':
        # print("Raw Data Example:", data[0:50,1])
        # print("bits: ", bits)
        # print("SampleWidth:",self.pa.get_sample_size(pyaudio.paInt16))
        data = data/(2**(bits-1))
    if return_nbits:
        return data, fs, bits 
    else:
        return data, fs


def plot_waveform(wav_file_name):
    cwd = os.path.abspath('.')
    wav_name = wav_file_name 
    wav_file_path = str(cwd) + '/Voice_WAV/wav_experiment/' + wav_file_name

    audio_data, fs, n_nbits = audio_read(wav_file_path)

    if np.abs(np.max(audio_data)) >= np.abs(np.min(audio_data)):
        MAX = np.abs(np.max(audio_data))
    elif np.abs(np.max(audio_data)) < np.abs(np.min(audio_data)):
        MAX = np.abs(np.min(audio_data))

    # normalization
    audio_data /= MAX 

    data_number = len(audio_data)

    time_sequence = np.linspace(0,data_number/fs,data_number)

    plt.figure(figsize=[20,10])

    plt.plot(time_sequence ,audio_data,color='darkviolet',label="")
    plt.ylim([-1,1])

    plt.xlim(time_sequence[0],time_sequence[-1])

    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)
      
    plt.ylabel('Amplitude', fontsize = 20)
    plt.xlabel('Time (second)', fontsize = 20)
    plt.title("Audio Wavform for Experiment 2",fontsize = 25)
    plt.legend(fontsize = 15)    

    # pass 
    cwd = os.path.abspath('.')
    fig_name = str(cwd) + '/PNG_voice_0311/' + str(wav_name) + '.png'
    plt.savefig(fig_name,dpi=600)

    plt.show()


if __name__ == '__main__':
    wav_file = '20230312-exp_2_OK_1.wav'
    plot_waveform(wav_file)
    
    # pass


