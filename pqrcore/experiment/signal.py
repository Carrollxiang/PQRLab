# -*- coding: utf-8 -*-
"""
Created on 2020-04-10

@author: 张宽

实验信号处理
"""

from math import inf
from pqrcore.expression import isname, ParsedExpression


class Signal():
    """
    单通道连续信号
    self._sig - 连续信号 (ParsedExpression类)
    """

    def __init__(self, sig):
        self.signal = sig

    def __str__(self):
        return str(self._sig)

    def __call__(self, *times, **rules):
        """
        计算self.signal的实时电压
        times = [t_0, t_1, t_2, ...]
            t_0 - 从当前连续信号开始的时间
            t_1 - 从当前所在最内层循环开始的时间
            t_2 - 从更外一层循环开始的时间
            ...
        """
        i = 0
        for time in times:
            rules['t_%u' % i] = time
            i += 1
        return self._sig(**rules)

    @property
    def signal(self):
        return self._sig

    @signal.setter
    def signal(self, sig):
        if not isinstance(sig, ParsedExpression):
            sig = ParsedExpression(sig)
        self._sig = sig


class LoopedSignal(Signal):
    """
    单通道循环信号
    self._sig = [(sig, t), ...] - 循环内容
        sig - 当前信号从前一段的t开始 (Signal类)
        t - 当前sig结束时间，t=0为本次循环开始时刻 (float,str类)
    self.__loops - 循环次数 (int,str类或inf)
    """

    def __init__(self, sig, loops):
        self.signal = sig
        self.loops = loops

    def __str__(self):
        def str_with_indent(sig, indent):
            """将sig输出为字符串表达式，加缩进"""
            string = 'loops = %u:' % sig.__loops
            d = 0.
            for sig, t in sig._sig:
                string += '\n' + indent * '    '
                string += '%.3f <= t < %.3f, ' % (d, t)
                if isinstance(sig, LoopedSignal):
                    string += str_with_indent(sig, indent + 1)
                else:
                    string += str(sig)
                d = t
            return string

        return str_with_indent(self, 1)

    def __call__(self, t, *times, **rules):
        """
        计算self.signal的实时电压
        t - 从第一次循环开始的时间，通过t可以计算t_0, t_1, ..., t_i
        times = [t_i+1, t_i+2, ...]
        """
        loops = self.__loops
        if isinstance(loops, str):
            loops = rules[loops]
        sig = self._sig
        d = sig[-1][1]
        if isinstance(d, str):
            d = rules[d]
        if t >= loops * d:
            return 0
        t_i = t % d
        d = 0.
        for sig, t in sig:
            if isinstance(t, str):
                t = rules[t]
            if t > t_i:
                t = t_i - d
                break
            d = t
        return sig(t, t_i, *times, **rules)

    @property
    def signal(self):
        return self._sig

    @signal.setter
    def signal(self, sig):
        self._sig = []
        d = 0.
        for sig, t in sig:
            try:
                t = float(t)
            except ValueError as err:
                if not isname(t):
                    raise err
            else:
                if t <= d:
                    continue
                d = t
            if not isinstance(sig, Signal):
                sig = Signal(sig)
            self._sig.append((sig, t))

    @property
    def loops(self):
        return self.__loops

    @loops.setter
    def loops(self, loops):
        try:
            loops = int(loops)
        except OverflowError:
            loops = inf
        except ValueError as err:
            if not isname(loops):
                raise err
        else:
            if loops < 0:
                raise ValueError('循环信号循环次数不能<0')
        self.__loops = loops
