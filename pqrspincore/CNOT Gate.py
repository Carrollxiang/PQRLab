import numpy as np


import ctypes


import re


import pqrspincore.DecodeSignal as ds


from pqrcore.experiment.signal import Signal, LoopedSignal


from math import inf


from pqrspincore.spinapi import *


# simple_loop = LoopedSignal([("0", 20), ("1", 150), ("0", 300)], 3)
# simple_loop2 = LoopedSignal([("0", 10), ("1", 50), ("0", 140), ("1", 210), ("1", 300)], 3)


L = 7330*ns

probe780 = LoopedSignal(
    [
        ('0', 535*ns),
        ('1', 535*ns+350*ns),
        ('0', 535*ns+350*ns+4610*ns),
        ('1', 535*ns+350*ns+4610*ns+350*ns),
        ('0', L)
    ], 4)

couping480 = LoopedSignal(
    [
        ('0', 10*ns),
        ('1', 150*ns),
        ('0', L)
    ], 4)

cooling = LoopedSignal(
    [
        ('0', 300*ns),
        ('1', 300*ns+350*ns),
        ('0', 300*ns+350*ns+4610*ns),
        ('1', 300*ns+350*ns+4610*ns+350*ns),
        ('0', L)
    ], 4)

readout480 = LoopedSignal(
    [
        ('0', 885 * ns),
        ('1', 885 * ns+1000 * ns),
        ('0', 885 * ns+1000*ns+3960*ns),
        ('1', 885 * ns+1000*ns+3960*ns+1210*ns),
        ('0', L)
    ], 4)


probefiber = LoopedSignal(
    [
        ('0', 300*ns),
        ('1', 300*ns+485*ns),
        ('0', 300*ns+485*ns+4475*ns),
        ('1', 300*ns+485*ns+4475*ns+485*ns),
        ('0', L)
    ], 4)

photonfiber = LoopedSignal(
    [
        ('0', 1145*ns),
        ('1', 1145*ns+740*ns),
        ('0', 1145*ns+740*ns+4220*ns),
        ('1', 1145*ns+740*ns+4220*ns+950*ns),
        ('0', L)
    ], 4)

gate = LoopedSignal(
    [
        ('0', 6520*ns),
        ('1', 6520*ns+250*ns),
        ('0', L)
    ], 4)

alwayson = LoopedSignal(
    [
        ("1", L)
    ], 4)

trigger = LoopedSignal(
    [
        ('0', 5260*ns),
        ('1', 5260*ns+235*ns),
        ('0', L)
    ], 4)

unkown = LoopedSignal(
    [
        ('0', 300*ns),
        ('1', 300*ns+1585*ns),
        ('0', L)
    ], 4)

LoopedSignal(
    [
        (LoopedSignal(
    [
        ('0', 300*ns),
        ('1', 300*ns+1585*ns),
        ('0', L)
    ], 4), 5260*ns),
        ('1', 5260*ns+235*ns),
        ('0', L)
    ], 4)


AllSignals = [[5, unkown, 0],
              [9, probe780, 0],
              [11, photonfiber, 0],
              [12, alwayson, 0],  # dipole
              [13, cooling, 0],
              [14, readout480, 0],
              [15, trigger, 0],
              [16, probefiber, 0],
              [17, gate, 0],
              [18, gate, 0],
              [19, gate, 0],
              [20, gate, 0],
              [22, alwayson, 0],
              [23, alwayson, 0],
              [24, alwayson, 0]
]



# t = ds.decode_multi_loop(pump)
# at = ds.adjust_general_delay(t, 1*us, 20*us)
#
# y = ds.decode_multi_loop(probe)
# ay = ds.adjust_general_delay(y, 3*us, 20*us)
#
# f = ds.decode_multi_loop(fuck)
# af = ds.adjust_general_delay(f, 1*us, 20*us)

# ds.synchronize_complex_sqeuence([[1, at], [2, ts]])
# chs = load_channels(AllSignals)


def QWP(theta):
    mat = [[1-1j*np.cos(theta*2), -1j*np.sin(theta*2)],
           [-1j*np.sin(theta*2), 1+1j*np.cos(theta*2)]]
    return np.array(mat)/np.sqrt(2)


def HWP(theta):
    mat = [[np.cos(theta), np.sin(theta)],
           [np.sin(theta), -np.cos(theta)]]
    return np.array(mat)


def ratate(alpha):
    mat1 = QWP(0)
    mat2 = HWP(alpha)
    mat = np.dot(mat1, mat2)
    return mat

