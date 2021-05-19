# -*- coding: utf-8 -*-
"""
Created on 2021-01-03

@author: 项德生

快时序接口
"""

from generator import GeneratorChannel


from experiment.signal import Signal, LoopedSignal


import matplotlib.pyplot as plt


import re


from math import inf



def encode_signal(sig):
    """
    加密信号
        sig - 信号 (Signal类)
        f_sysclk - 内部时钟频率以MHz为单位 (float类)
        enable_profile_asf - 是否使能单音profiles调制幅度 (bool类)
        enable_sine_out - 选择DDS正弦波输出位 (bool类)
    返回
        val - 寄存器值 (int类)
    """
    if isinstance(sig, Signal):
        while isinstance(sig, LoopedSignal):
            sig = sig.signal[-1][0]
    else:
        sig = Signal(sig)
    expr = sig.signal.expression
    print(expr)


sig = LoopedSignal(
    [
    #前100微秒准备
    (0, 100),
    #循环5次快时序
    (LoopedSignal(
        [
            ('1', 50),
            ('2', 100),
            ('3', 250)
        ], 4)
    , 1100),
    (0, 2100),
    #循环5次快时序
    (LoopedSignal(
        [
            (LoopedSignal([("4", 100)], 2), 200),
            ('2', 300),
            ('3', 450)
        ], 4)
    , 3100),
    (0, 4100),
    (0, 5100),
    ], 2)

# --------signal作图-----------
# print(sig._sig[1][0]._sig[0][0].signal.expression)
# plt.plot(
#     range(2500),
#     [sig(t) for t in range(2500)]
#     )
# plt.show()

depth = 0
def expand_loopedsignal(ALoopedSignal,depth):
    print("Start Loop")  # 声明Loop开始
    for k in ALoopedSignal._sig:
        if type(k[0]) == Signal:
            print(str(type(k[0]))+" depth = " + str(depth))
            end_time = k[1]
            previous_index = ALoopedSignal._sig.index(k)-1
            if previous_index < 0:
                start_time = 0
            else:
                start_time = ALoopedSignal._sig[previous_index][1]
            print(end_time-start_time)
        else:
            expand_loopedsignal(k[0], depth+1)  # 递归,深度加一
        if ALoopedSignal._sig.index(k) == len(ALoopedSignal._sig)-1:  # 声明Loop结束
            print("End Loop")


expand_loopedsignal(sig, depth)

