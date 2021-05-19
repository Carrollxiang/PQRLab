# -*- coding: utf-8 -*-
"""
Created on 2020-04-21

@author: 张宽

设备包括发生器、探测器、监视器等
"""

import weakref


class Channel():
    """
    通道基础类
    self.__dev - 从属设备的弱引用 (weakref类)
    self.__ch - 通道信息，如编号 (int类)、描述 (str类)
    """

    def __new__(cls, dev, ch):
        """通道只能由其从属设备创建"""
        if dev in dev.gets():
            return dev[ch]
        self = super().__new__(cls)
        self.__dev = weakref.ref(dev)
        self.__ch = ch
        return self

    def __str__(self):
        return '%s[%s]' % (self.device, self.__ch)

    @property
    def device(self):
        return self.__dev()

    @property
    def channel(self):
        return self.__ch


class Device():
    """
    设备基础类
    cls._devs = {(brand, model, sn): dev, ...} - 设备注册表
         brand - 厂商 (str类)
        model - 型号 (str类)
        sn - 序列号 (str类)
        dev - 设备 (Device类)
    cls._ch_type - 设备通道类型 (type类 = Channel或其子类)
    cls._chs = [ch, ...]
        ch - 通道信息，如编号 (int类)、描述 (str类)
    self.__brand - 厂商 (str类)
    self.__model - 型号 (str类)
    self.__sn - 序列号 (str类)
    self.__chs = {ch: chan, ...} - 全部通道
        ch - 通道信息，如编号 (int类)、描述 (str类)
        chan - 通道 (Channel类)
    self.__name - 设备名 (str类)
    self._handle (int类)
    """
    _devs = {}
    _ch_type = Channel
    _chs = []

    def __new__(cls, brand, model, sn, name='', handle=-1):
        devs = Device._devs
        brand = str(brand)
        model = str(model)
        sn = str(sn)
        try:
            self = devs[brand, model, sn]
        except KeyError:
            self = super().__new__(cls)
            self.__brand = brand
            self.__model = model
            self.__sn = sn
            self.__chs = chs = {}
            for ch in cls._chs:
                chs[ch] = self._ch_type(self, ch)
            self._handle = int(handle)
            devs[brand, model, sn] = self
        else:
            if type(self) != cls:
                raise TypeError('%s不是%s类' % (self, cls.__name__))
            if self._handle != handle:
                raise KeyError('%s的%s序列号重复' % (brand, model))
        self.name = name
        return self

    def __str__(self):
        if self.__name == '':
            return '%s_%s_%s' % (self.__brand, self.__model, self.__sn)
        return self.__name

    def __len__(self):
        return len(self.__chs)

    def __getitem__(self, ch):
        return self.__chs[ch]

    def __iter__(self):
        return iter(self.__chs.values())

    def __contains__(self, chan):
        return chan in self.__chs.values()

    @property
    def brand(self):
        return self.__brand

    @property
    def model(self):
        return self.__model

    @property
    def serial_number(self):
        return self.__sn

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = str(name)

    @classmethod
    def get(cls, *args):
        """返回指定设备"""
        return cls._devs[args]

    @classmethod
    def gets(cls):
        """返回全部设备列表"""
        return list(cls._devs.values())

    def delete(self):
        """删除设备"""
        brand = self.__brand
        model = self.__model
        sn = self.__sn
        del Device._devs[brand, model, sn]
