import numpy as np


import pqrspincore.DecodeSignal as ds


from pqrcore.experiment.signal import Signal, LoopedSignal


from pqrspincore.spinapi import *


unit_list = {
    'ns': 1.0,
    'us': 1000.0,
    'ms': 1000000.0
}

channel_list = {
    '0': 'scmos',
    '1': 'cooling_780',
    '2': 'repump_780',
    '3': 'EOM_ttl',
    '4': 'depump_back_795',
    '5': 'depump_front_795',
    '6': 'repump_795',
    '7': 'state_prepare_795',
    '8': 'probe_space_AOM_780',
    '9': 'reset',
    '10': 'single_photon_AOM',
    '11': 'v_dipole',
    '12': 'detune_480',
    '13': 'readout_480',
    '14': 'qutau_trigger',
    '15': 'probe_fiber_AOM_780',
    '16': 'spd_gate',
    '17': 'spd_gate',
    '18': 'spd_gate',
    '19': 'spd_gate',
    '20': 'unused',
    '21': 'always_on',
    '22': 'always_on',
    '23': 'always_on',
}

def new_get_pb_data(line):
    label = re.findall(r"^[a-zA-z]+", line)
    if len(label) != 0:
        label = label[0]
    else:
        label = ''

    output_pattern = re.findall(r"0b[\w\s]+", re.findall(r"0b[\w\s]+\,", line)[0])[0].replace(' ', '')  # 2进制
    # output_pattern = re.findall(r"0x[a-zA-Z0-9]+", line)[0].replace(' ','')  # 16进制
    time = re.findall(r"[0-9]+", re.findall(r"\,\s*[0-9]+", line)[0])[0]
    unit = re.findall(r"[a-z]s", re.findall(r"[0-9][a-z]s", line)[0])[0]

    inst = re.findall(r"\,\s*[a-zA-z]+\,*?", line)
    if len(inst) != 0:
        inst = inst_dict[re.findall(r"[a-zA-z]+", re.findall(r"\,\s*[a-zA-z]+\,*?", line)[0])[0]]
        inst_data = re.findall(r"\,\s*[0-9]+\s*//", line)
        if len(inst_data) != 0:
            inst_data = int(re.findall(r"[0-9]+", inst_data[0])[0])
        else:
            inst_data = 0
    else:
        inst = 0
        inst_data = 0
    # comment = re.findall(r"//.*", line)
    return output_pattern, time, inst, inst_data, unit

# str1 = 'mininal_time_sequence.pb'
# channels = [[] for i in range(24)]
#
# with open(str1, 'r+', encoding='UTF-8') as file:
#     for line in file:
#         if len(line.strip()) != 0:
#             pattern = new_get_pb_data(line)[0]
#             time = new_get_pb_data(line)[1]
#             inst = int(new_get_pb_data(line)[2])
#             inst_data = int(new_get_pb_data(line)[3])
#             unit = unit_list[new_get_pb_data(line)[4]]
#             for i in range(24):
#                 channels[i].append(np.array([int(pattern[i+2]), int(time)*unit, inst, inst_data]))
#
# for i in range(24):
#     channels[i] = np.vstack(channels[i])
#     channels[i] = ds.combine_similar_items(channels[i])
#     temp = []
#     for j in range(channels[i].shape[0]):
#         temp.append((str(channels[i][j][0]), channels[i][j][1]))
#     # print(temp)
#     channels[i] = temp
#     print(channel_list[str(23-i)], '=LoopedSignal(', channels[i], ',5)')
#
#
# LoopedSignal_list = [LoopedSignal(channels[i], 4)for i in range(24)]

# file = open('my.txt', 'w+')
# for i in range(len(data)):
#     s = str(data[i]).replace('[','').replace(']','')#去除[],这两行按数据不同，可以选择
#     s = s.replace("'",'').replace(',','') +'\n'   #去除单引号，逗号，每行末尾追加换行符
#     file.write(s)
# file.write(LoopedSignal_list)
# file.close()




