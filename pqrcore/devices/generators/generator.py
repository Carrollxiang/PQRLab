# -*- coding: utf-8 -*-
"""
Created on 2020-04-21

@author: 张宽

信号发生器
"""

from devices.device import Channel, Device
from experiment.signal import Signal


class GeneratorChannel(Channel):
    """
    发生器通道基础类
    self._sig: 已加载的信号
    """

    @property
    def signal(self):
        try:
            sig = self._sig
        except AttributeError:
            sig = Signal(0)
        return sig

    @signal.setter
    def signal(self, sig):
        if not isinstance(sig, Signal):
            sig = Signal(sig)
        self._sig = sig


class Generator(Device):
    """发生器基础类"""
    _ch_type = GeneratorChannel

    @property
    def signals(self):
        sigs = {}
        for ch in self:
            sigs[ch] = ch.signal
        return sigs

    @signals.setter
    def signals(self, sigs):
        sig = Signal(0)
        for ch in self:
            ch.signal = sigs.get(ch, sig)
