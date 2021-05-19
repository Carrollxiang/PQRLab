from pqrcore.experiment.signal import Signal, LoopedSignal

import re

from math import inf

import numpy as np

ns = 1.0
us = 1000.0
ms = 1000000.0

MHz = 1.0
kHz = 0.001
Hz = 0.000001


def encode_signal(sig):
    """
        sig - 信号 (Signal类)
    """
    if isinstance(sig, Signal):
        while isinstance(sig, LoopedSignal):
            sig = sig.signal[-1][0]
    else:
        sig = Signal(sig)
    expr = sig.signal.expression
    print(expr)




def is_single_loop(ALoopedSignal):
    simple_bool = True
    if type(ALoopedSignal) == LoopedSignal:
        for i in range(len(ALoopedSignal.signal)):
            k = ALoopedSignal.signal[i]
            if type(k[0]) != Signal:  # 判断是否为简单循环
                simple_bool = False
                break
    elif type(ALoopedSignal) == np.ndarray:
        for i in range(ALoopedSignal.shape[0]):
            if ALoopedSignal[i, 2] != 0:  # 判断是否为简单循环
                simple_bool = False
                break
    else:
        raise ValueError("传参类型不对！")
        return -1
    return simple_bool


def decode_simple_loop(ALoopedSignal):
    """
    处理简单循环
        sequence1[on/off , duration, inst, inst_data] - 单通道序列
        lasting_time - 循环一次持续时间
        loop_times - 循环次数
    :param ALoopedSignal:
    :return:
    """
    if type(ALoopedSignal) != LoopedSignal:
        raise ValueError("传参类型不对！")

    if len(ALoopedSignal.signal) == 1:
        sequence = np.array([ALoopedSignal.signal[0][0].signal.expression,  # 将第一行写入序列
                              ALoopedSignal.signal[0][1], -1, 0])
        lasting_time = ALoopedSignal.signal[0][1]
        loop_times = 0
        return sequence, lasting_time, loop_times

    sequence1 = np.array([ALoopedSignal.signal[0][0].signal.expression,  # 将第一行写入序列
                          ALoopedSignal.signal[0][1]])
    if len(ALoopedSignal.signal) == 2:
        temp = np.array([ALoopedSignal.signal[1][0].signal.expression,  # 将第二行写入序列
                         ALoopedSignal.signal[1][1] - ALoopedSignal.signal[0][1]])
        sequence1 = np.vstack((sequence1, temp))
    else:
        for i in range(len(ALoopedSignal.signal) - 1):
            temp = np.array([ALoopedSignal.signal[i + 1][0].signal.expression,  # 将第一行写入序列
                             ALoopedSignal.signal[i + 1][1] - ALoopedSignal.signal[i][1]])
            sequence1 = np.vstack((sequence1, temp))
    status = np.zeros((len(ALoopedSignal.signal), 2))
    status[0][0] = 2  # 声明循环开始
    status[0][1] = ALoopedSignal.loops  # 声明循环次数
    status[-1][0] = 3  # 声明循环结束
    sequence1 = np.hstack((sequence1, status))  # 合并sequence和status
    lasting_time = ALoopedSignal.signal[-1][1]
    loop_times = ALoopedSignal.loops
    return sequence1, lasting_time, loop_times


def adjust_limit_loop(ALoopedSignal, limited_time):
    """
    处理有时长限制的简单循环
    :param ALoopedSignal:可以是signal类,也可以是np.array类
    :param limited_time: 循环的限制时间
    :return:
    """
    if type(ALoopedSignal) == LoopedSignal:
        simple_sequence, lasting_time, loop_times = decode_simple_loop(ALoopedSignal)
    elif type(ALoopedSignal) == np.ndarray:
        simple_sequence = ALoopedSignal
        lasting_time = sum(ALoopedSignal[:, 1])
        loop_times = ALoopedSignal[0, 3]
    else:
        raise ValueError("传参类型不对！")
        return -1

    if lasting_time*loop_times == limited_time:
        return simple_sequence

    elif lasting_time*loop_times > limited_time:  # 循环时长超过限制时长，需要缩短序列
        mismatch_time = lasting_time*loop_times - limited_time
        reduced_times = 1 + mismatch_time // lasting_time
        if loop_times <= reduced_times:
            raise ValueError("时序长度不对!")
        else:
            simple_sequence[0, 3] -= reduced_times
            mismatch_time = limited_time - limited_time // lasting_time * lasting_time
            temp = 0
            add_sequence = np.array([0, 0, 0, 0])
            for i in range(simple_sequence.shape[0]):
                temp += simple_sequence[i][1]
                if temp <= mismatch_time:
                    inst = np.array([simple_sequence[i][0], simple_sequence[i][1], 0, 0])
                    add_sequence = np.vstack((add_sequence, inst))
                else:
                    inst = np.array([simple_sequence[i][0], mismatch_time - (temp - simple_sequence[i][1]), 0, 0])
                    add_sequence = np.vstack((add_sequence, inst))
                    break
            simple_sequence = np.vstack((simple_sequence, add_sequence[1:, :]))

            lens = len(simple_sequence)
            for j in range(lens):
                t = lens - j - 1
                if simple_sequence[t, 1] == 0:
                    simple_sequence = np.delete(simple_sequence, t, axis=0)  # 去除序列中时间为0的部分
            return simple_sequence

    else:  # 循环时长小于限制时长，需要扩增序列
        mismatch_time = abs(lasting_time*loop_times - limited_time)
        zero_sequence = np.array([0, mismatch_time, 0, 0])
        simple_sequence = np.vstack((simple_sequence, zero_sequence))
        return simple_sequence


def combine_similar_items(sequence):
    '''
    合并冗余项
    :param sequence: 未处理序列
    :return:
    '''
    if len(sequence.shape) ==1:
        return sequence

    while True:  # 合并冗余语句
        have_similar_items = False
        for i in range(sequence.shape[0] - 1):  # 全部遍历，检测是否能合并语句
            if sequence[i, 0] == sequence[i + 1, 0] and sequence[i, 2] == sequence[i + 1, 2] == 0:
                have_similar_items = True

        if not have_similar_items:
            break

        for i in range(sequence.shape[0] - 1):
            if sequence[i, 0] == sequence[i + 1, 0] and sequence[i, 2] == sequence[i + 1, 2] == 0:
                sequence[i, 1] += sequence[i + 1, 1]
                sequence = np.delete(sequence, i + 1, axis=0)
                break
    lens = sequence.shape[0]
    for j in range(lens):
        i = lens - j - 1
        if sequence[i, 1] == 0:
            sequence = np.delete(sequence, i, axis=0)  # 删除无效声明
    if sequence[0, 1] == 0:
        sequence = np.delete(sequence, 0, axis=0)
    return sequence


def edge_detect(f):
    '''
    :param f:
    :return:
    '''
    N = len(f)
    edge = np.zeros((N - 1))
    for i in range(N - 1):
        edge[i] = f[i] - f[i + 1]
    return edge


def adjust_loop_delay(loop_sequence, delay):
    """
    考虑延迟后将简单循环进行错位
    默认响应延迟时间要小于单次循环时间！
    :param loop_sequence: 需要错位的简单循环
    :param delay: 本通道的响应延迟
    :return: adjusted_sequence: 调整后的时间序列
    """
    if delay == 0:
        return loop_sequence
    loop_times = loop_sequence[0, 3]
    front_sequence = np.array([0, 0])
    temp = 0
    middle_sequence = loop_sequence[:, 0:2]
    end_sequence = loop_sequence[:, 0:2]
    for i in range(loop_sequence.shape[0]):
        temp += loop_sequence[i, 1]
        if temp <= delay:
            insert_sequence = loop_sequence[i, 0:2]
            # print(front_sequence, insert_sequence)
            front_sequence = np.vstack((front_sequence, insert_sequence))
            middle_sequence = np.delete(middle_sequence, 0, axis=0)
            middle_sequence = np.vstack((middle_sequence, insert_sequence))
            end_sequence = np.delete(end_sequence, 0, axis=0)
        else:
            if temp == loop_sequence[i-1, 1]+delay:
                break
            mismatch_time = temp - delay
            insert_sequence = np.array([loop_sequence[i, 0], delay])
            complementary_sequence = np.array([loop_sequence[i, 0], mismatch_time])
            front_sequence = np.vstack((front_sequence, insert_sequence))
            middle_sequence = np.delete(middle_sequence, 0, axis=0)
            middle_sequence = np.vstack((complementary_sequence, middle_sequence))
            middle_sequence = np.vstack((middle_sequence, insert_sequence))
            end_sequence = np.delete(end_sequence, 0, axis=0)
            end_sequence = np.vstack((complementary_sequence, end_sequence))
            break

    front_status = np.zeros((front_sequence.shape[0], 2))
    middle_status = np.zeros((middle_sequence.shape[0], 2))
    end_status = np.zeros((end_sequence.shape[0], 2))

    front_sequence = np.hstack((front_sequence, front_status))
    middle_sequence = np.hstack((middle_sequence, middle_status))
    end_sequence = np.hstack((end_sequence, end_status))

    middle_sequence[0, 2] = 2
    middle_sequence[0, 3] = loop_times - 1
    middle_sequence[-1, 2] = 3

    adjusted_sequence = np.vstack((front_sequence, middle_sequence, end_sequence))
    adjusted_sequence = combine_similar_items(adjusted_sequence)
    # print('front_sequence', front_sequence)
    # print("middle_sequence", middle_sequence)
    # print('end_sequence', end_sequence)
    return adjusted_sequence


def adjust_simple_delay(simple_sequence, delay):
    '''
    处理简单序列的延迟问题
    :param simple_sequence: 简单序列
    :param delay: 延迟
    :return:
    '''
    if delay == 0:
        return simple_sequence
    lens = simple_sequence.shape[0]
    edge = edge_detect(simple_sequence[:, 0])
    insert_number = 0
    for i in range(lens - 1):
        if edge[i] == -1:
            temp = np.array([0, edge[i] * delay, 0, 0])
            simple_sequence = np.insert(simple_sequence, i + insert_number + 1, temp, axis=0)
            insert_number += 1
        elif edge[i] == 1:
            temp = np.array([0, edge[i] * delay, 0, 0])
            simple_sequence = np.insert(simple_sequence, i + insert_number + 1, temp, axis=0)
            insert_number += 1
    simple_sequence = combine_similar_items(simple_sequence)
    return simple_sequence


def adjust_general_delay(sequence, delay, max_delay):
    if len(sequence.shape) == 1:
        sequence[1] += max_delay
        sequence = combine_similar_items(sequence)
        return sequence
    sequence = np.vstack((np.array([0, max_delay, 0, 0]), sequence))
    if delay == 0:
        sequence = combine_similar_items(sequence)
        return sequence

    index_split = []  # 切割序列

    sequence_start = 0
    sequence_end = 0
    loop_start = 0
    loop_end = 0
    state = sequence[:, 2]


    if is_single_loop(sequence):
        index_split.append([0, sequence.shape[0], "simple_sequence"])
    else:
        for i in range(sequence.shape[0]):
            if state[i] == 2:
                loop_start = i
                sequence_end = i - 1
                index_split.append([sequence_start, sequence_end, "simple_sequence"])
            if state[i] == 3:
                loop_end = i
                sequence_start = i + 1
                index_split.append([loop_start, loop_end, "loop"])
        if loop_end < len(state) - 1:
            index_split.append([loop_end + 1, len(state) - 1, "simple_sequence"])
    new_sequence = np.array([0, 0, 0, 0])

    for x in index_split:
        temp = sequence[x[0]:x[1]+1, :]
        if x[2] == "simple_sequence":
            if x[0] != 0:
                temp = np.vstack((np.array([1, 0, 0, 0]), temp))
            if x[1] != len(state):
                temp = np.vstack((temp, np.array([1, 0, 0, 0])))
            # print(adjust_simple_delay(temp, delay))
            new_sequence = np.vstack((new_sequence, adjust_simple_delay(temp, delay)))
        if x[2] == "loop":
            # print(adjust_loop_delay(temp, delay))
            new_sequence = np.vstack((new_sequence, adjust_loop_delay(temp, delay)))
    new_sequence = np.vstack((new_sequence, np.array([0, delay, 0, 0])))  # 补足时序长度
    sequence = combine_similar_items(new_sequence)

    return sequence


def decode_multi_loop(ALoopedSignal):
    """
    大循环中有多个一级小循环
    :param ALoopedSignal: 两层嵌套循环
    :return: sequence: 两层单通道序列(不考虑延迟)
    """
    if len(ALoopedSignal.signal) == 1:
        sequence = decode_simple_loop(ALoopedSignal)[0]
        return sequence
    sequence = np.array([0, 0, 0, 0])  # 空白序列
    for i in range(len(ALoopedSignal.signal)):  # 解包双层循环
        k = ALoopedSignal.signal[i]
        if i == 0:
            begin_time = 0
        else:
            p = ALoopedSignal.signal[i - 1]
            begin_time = p[1]  # 上次状态的结束时间
        if type(k[0]) == Signal:
            temp = np.array([k[0].signal.expression, k[1] - begin_time, 0, 0])
            sequence = np.vstack((sequence, temp))
            # print('Signal', temp)
        else:
            temp = adjust_limit_loop(k[0], k[1] - begin_time)
            sequence = np.vstack((sequence, temp))
            # print('Loop', k[0], k[1] - begin_time)
    sequence = np.delete(sequence, 0, axis=0)  # 删除补位空序列

    while True:  # 展开小于等于两次的循环
        have_useless_loop = False
        for i in range(sequence.shape[0]):  # 全部遍历，检测是否有小于两次的循环
            if 0 < sequence[i, 3] < 3:
                have_useless_loop = True

        if not have_useless_loop:
            break

        for i in range(sequence.shape[0]):
            if 0 < sequence[i, 3] < 3:
                loop_times = sequence[i, 3]
                find_min = True
                nearest_index = 0
                while find_min:
                    if sequence[i + nearest_index, 2] == 3:
                        find_min = False
                    else:
                        nearest_index += 1
                if loop_times == 1:
                    sequence[i, 3] = 0
                    sequence[i, 2] = 0
                    sequence[i + nearest_index, 2] = 0
                else:
                    sequence[i, 3] = 0
                    sequence[i, 2] = 0
                    sequence[i + nearest_index, 2] = 0
                    for k in range(nearest_index + 1):
                        sequence = np.insert(sequence, i + nearest_index + k + 1, sequence[i + k, :], axis=0)
                break
    sequence = combine_similar_items(sequence)  # 合并同类项
    sequence[0, 2] = 2
    sequence[-1, 2] = 3
    sequence[0, 3] = ALoopedSignal.loops

    return sequence


def decode_recursion_loop(ALoopedSignal):
    """
    未开发成功
    :param ALoopedSignal:
    :return:
    """
    # for k in ALoopedSignal._sig:
    #     if type(k[0]) == Signal:
    #         print(str(type(k[0]))+" depth = " + str(depth))
    #         end_time = k[1]
    #         previous_index = ALoopedSignal._sig.index(k)-1
    #         if previous_index < 0:
    #             start_time = 0
    #         else:
    #             start_time = ALoopedSignal._sig[previous_index][1]
    #         print(end_time-start_time)
    #     else:
    #         decode_recursion_loop(k[0], depth+1)  # 递归,深度加一
    #     if ALoopedSignal._sig.index(k) == len(ALoopedSignal._sig)-1:  # 声明Loop结束
    #         print("End Loop")
    if is_single_loop(ALoopedSignal):
        return decode_simple_loop(ALoopedSignal)[0]
    else:
        empty_sequence = np.array([0, 0, 0, 0])
        for i in range(len(ALoopedSignal.signal)):
            k = ALoopedSignal.signal[i]
            if i == 0:
                begin_time = 0
            else:
                p = ALoopedSignal.signal[i - 1]
                begin_time = p[1]  # 上次状态的结束时间
            limit_time = k[1] - begin_time
            if type(k[0]) == Signal:
                temp = np.array([k[0].signal.expression, limit_time, 0, 0])
                empty_sequence = np.vstack((empty_sequence, temp))
            else:
                return empty_sequence
        return empty_sequence


def synchronize_simple_sqeuence(sequence_list):
    """

    :param sequence_list: [[port_1,sequence_1]...[port_n,sequence_n]]
    :return:
    """
    timeline = [0]
    for channel_index, channel in enumerate(sequence_list):
        if len(channel[1].shape) == 1:
            timeline.append(channel[1][1])
            continue
        else:
            for index, instruction in enumerate(channel[1]):
                timeline.append(sum(channel[1][0:index, 1]))
        timeline.append(sum(channel[1][:, 1]))
    timeline = list(sorted(set(timeline)))
    cell_line = [timeline[i+1] - timeline[i] for i in range(len(timeline)-1)]
    all_channels = np.zeros((len(cell_line), 4))
    all_channels[:, 1] = cell_line

    for channel_index, channel in enumerate(sequence_list):
        port = channel[0]
        sequence = channel[1]
        split_sequence = []

        index = 0
        stat_index = 0
        sub_index = 0
        # print(sequence[:, 1])
        if len(sequence.shape) == 1:
            bin_list = ["0" for i in range(port-1)]
            bin_list.insert(0, "0b1")
            bin_str = "".join(bin_list)
            all_channels[:, 0] += int(bin_str, 2)
            continue
        while stat_index < sequence.shape[0]:
            part = []
            temp = 0
            while True:
                if sub_index + index == len(cell_line):
                    break
                temp += cell_line[index+sub_index]
                part.append(cell_line[index+sub_index])
                if temp < sequence[stat_index][1]:
                    sub_index += 1
                else:
                    split_sequence.append([sequence[stat_index][0], part])
                    break
            index += sub_index+1
            stat_index += 1
            sub_index = 0

        index = 0
        cell_index = 0
        while index < len(split_sequence):
            for i in range(len(split_sequence[index][1])):
                bin_list = ["0" for j in range(port - 1)]
                bin_list.insert(0, "0b"+str(int(split_sequence[index][0])))
                bin_str = "".join(bin_list)
                all_channels[cell_index, 0] += int(bin_str, 2)
                cell_index += 1
            index += 1

        # print("split_sequence", split_sequence)

    return all_channels


def synchronize_complex_sqeuence(sequence_list):
    """

    :param sequence_list: [[port_1,sequence_1]...[port_n,sequence_n]]
    :return:
    """
    part = [[] for i in sequence_list]
    all_channels = np.zeros((1, 4))
    special_channel = []
    normal_channel = []
    for index, ch in enumerate(sequence_list):
        index_split = part[index]  # 切割序列
        sequence = ch[1]
        if len(sequence.shape) == 1:
            special_channel.append(index)
            continue
        else:
            normal_channel.append(index)
        sequence_start = 0
        sequence_end = 0
        loop_start = 0
        loop_end = 0
        state = sequence[:, 2]
        if is_single_loop(sequence):
            index_split.append([0, sequence.shape[0], "simple_sequence"])
        else:
            for i in range(sequence.shape[0]):
                if state[i] == 2:
                    loop_start = i
                    sequence_end = i - 1
                    index_split.append([sequence_start, sequence_end, "simple_sequence"])
                if state[i] == 3:
                    loop_end = i
                    sequence_start = i + 1
                    index_split.append([loop_start, loop_end, "loop"])
            if loop_end < len(state) - 1:
                index_split.append([loop_end + 1, len(state) - 1, "simple_sequence"])
        # print(index_split)

    for i in range(len(part[0])):
        temp = []
        for k in range(len(part)):
            if k in special_channel:
                continue
            if len(sequence_list[k][1]) == 1:
                temp.append([sequence_list[k][0], sequence_list[k][1][0, :]])
            else:
                temp.append([sequence_list[k][0], sequence_list[k][1][part[k][i][0]:part[k][i][1]+1, :]])
        synchronized_sequence = synchronize_simple_sqeuence(temp)
        # print("synchronized_sequence", synchronized_sequence)
        if part[0][i][2] == 'loop':
            normal_index = normal_channel[0]
            synchronized_sequence[0, 2] = 2
            synchronized_sequence[0, 3] = sequence_list[normal_index][1][part[normal_index][i][0], 3]
            synchronized_sequence[-1, 2] = 3
        all_channels = np.vstack((all_channels, synchronized_sequence))
        # print("finish one part")

    for i in special_channel:
        port = sequence_list[i][0]
        bin_list = ["0" for i in range(port - 1)]
        bin_list.insert(0, "0b"+str(int(sequence_list[i][1][0])))
        bin_str = "".join(bin_list)
        all_channels[:, 0] += int(bin_str, 2)
    all_channels = combine_similar_items(all_channels)
    # print("all_channels", all_channels)
    return all_channels

