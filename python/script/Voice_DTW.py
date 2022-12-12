'''
Date: 2022-12-12 15:30:39
LastEditors: Guo Yuqin,12032421@mail.sustech.edu.cn
LastEditTime: 2022-12-12 16:23:02
FilePath: /script/Voice_DTW.py
'''

import numpy as np 

from scipy.signal import lfilter 

class Voice_DTW(object):
    
    # def __init__(self) -> None:
        # pass 

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


    def melbankm(self, p, NFFT, fs, fl, fh, w=None):
        """
        计算Mel滤波器组
        :param p: 滤波器个数
        :param n: 一帧FFT后的数据长度
        :param fs: 采样率
        :param fl: 最低频率
        :param fh: 最高频率
        :param w: 窗(没有加窗，无效参数)
        :return:
        """
        bl = 1125 * np.log(1 + fl / 700)  # 把 Hz 变成 Mel
        bh = 1125 * np.log(1 + fh / 700)
        B = bh - bl  # Mel带宽
        y = np.linspace(0, B, p + 2)  # 将梅尔刻度等间隔
        Fb = 700 * (np.exp(y / 1125) - 1)  # 把 Mel 变成Hz
        W2 = int(NFFT / 2 + 1)
        df = fs / NFFT
        freq = [int(i * df) for i in range(W2)]  # 采样频率值
        bank = np.zeros((p, W2))
        for k in range(1, p + 1):
            f0, f1, f2 = Fb[k], Fb[k - 1], Fb[k + 1]
            n1 = np.floor(f1 / df)
            n2 = np.floor(f2 / df)
            n0 = np.floor(f0 / df)
            for i in range(1, W2):
                if n1 <= i <= n0:
                    bank[k - 1, i] = (i - n1) / (n0 - n1)
                elif n0 < i <= n2:
                    bank[k - 1, i] = (n2 - i) / (n2 - n0)
                elif i > n2:
                    break
            # plt.plot(freq, bank[k - 1, :], 'r')
        # plt.savefig('images/mel.png')
        return bank


    def Nmfcc(self, x, fs, p, frameSize, inc, nfft=512, n_dct=12):
        """
        计算mfcc系数
        :param x: 输入信号
        :param fs: 采样率
        :param p: Mel滤波器组的个数
        :param frameSize: 分帧的每帧长度
        :param inc: 帧移
        :return:
        """
        # 预处理-预加重
        xx = lfilter([1, -0.9375], [1], x)
        # 预处理-分幀
        xx = self.enframe(xx, frameSize, inc)
        # 预处理-加窗
        xx = np.multiply(xx, np.hanning(frameSize))
        # 计算FFT
        xx = np.fft.rfft(xx, nfft)
        # 计算能量谱
        xx = (np.abs(xx) ** 2) / nfft
        # 计算通过Mel滤波器的能量
        bank = self.melbankm(p, nfft, fs, 0, 0.5 * fs, 0)
        ss = np.matmul(xx, bank.T)
        # 计算DCT倒谱
        M = bank.shape[0]
        m = np.array([i for i in range(M)])
        mfcc = np.zeros((ss.shape[0], n_dct))
        for n in range(n_dct):
            mfcc[:, n] = np.sqrt(2 / M) * np.sum(np.multiply(np.log(ss), np.cos((2 * m - 1) * n * np.pi / 2 / M)), axis=1)
        return mfcc


    def myDTW(self, F, R):
        """
        动态时间规划
        :param F:为模板MFCC参数矩阵
        :param R:为当前语音MFCC参数矩阵
        :return:cost为最佳匹配距离
        """
        r1, c1 = F.shape
        r2, c2 = R.shape
        distence = np.zeros((r1, r2))
        for n in range(r1):
            for m in range(r2):
                FR = np.power(F[n, :] - R[m, :], 2)
                distence[n, m] = np.sqrt(np.sum(FR)) / c1

        D = np.zeros((r1 + 1, r2 + 1))
        D[0, :] = np.inf
        D[:, 0] = np.inf
        D[0, 0] = 0
        D[1:, 1:] = distence

        # 寻找整个过程的最短匹配距离
        for i in range(r1):
            for j in range(r2):
                dmin = min(D[i, j], D[i, j + 1], D[i + 1, j])
                D[i + 1, j + 1] += dmin

        cost = D[r1, r2]
        return cost


    def deltacoeff(self, x):
        """
        计算MFCC差分系数
        :param x:
        :return:
        """
        nr, nc = x.shape
        N = 2
        diff = np.zeros((nr, nc))
        for t in range(2, nr - 2):
            for n in range(N):
                diff[t, :] += n * (x[t + n, :] - x[t - n, :])
            diff[t, :] /= 10
        return diff


    def mfccf(self, num, s, Fs):
        """
        计算并返回信号s的mfcc参数及其一阶和二阶差分参数
        :param num:
        :param s:
        :param Fs:
        :return:
        """
        N = 512  # FFT数
        Tf = 0.02  # 窗口的时长
        n = int(Fs * Tf)  # 每个窗口的长度
        M = 24  # M为滤波器组数
        l = len(s)
        Ts = 0.01  # 帧移时长
        FrameStep = int(Fs * Ts)  # 帧移
        lifter = np.array([i for i in range(num)])
        lifter = 1 + int(num / 2) * np.sin(lifter * np.pi / num)

        if np.mean(np.abs(s)) > 0.01:
            s = s / np.max(s)
        # 计算MFCC
        mfcc = self.Nmfcc(s, Fs, M, n, FrameStep)

        mfcc_l = np.multiply(mfcc, lifter)
        d1 = self.deltacoeff(mfcc_l)
        d2 = self.deltacoeff(d1)
        return np.hstack((mfcc_l, d1, d2))


    def CMN(r):
        """
        归一化
        :param r:
        :return:
        """
        return r - np.mean(r, axis=1, keepdims=True)


    def DTWScores(self, r, features, N):
        """
        DTW寻找最小失真值
        :param r:为当前读入语音的MFCC参数矩阵
        :param features:模型参数
        :param N:为每个模板数量词汇数
        :return:
        """
        # 初始化判别矩阵
        scores1 = np.zeros(N)
        scores2 = np.zeros(N)
        scores3 = np.zeros(N)

        for i in range(N):
            scores1[i] = self.myDTW(self.CMN(features['p1_{}'.format(i)]), r)
            scores2[i] = self.myDTW(self.CMN(features['p2_{}'.format(i)]), r)
            scores3[i] = self.myDTW(self.CMN(features['p2_{}'.format(i)]), r)
        return scores1, scores2, scores3
