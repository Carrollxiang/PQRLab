import numpy as np


import pandas as pd


import os



def data_trans(filename):
    try:
        origin_data = pd.read_excel(filename, encoding='utf-8')
        del origin_data['Name']
        origin_data.replace(np.nan, 0, inplace=True)
        origin_data = origin_data.values
    except IOError:
        print("Error: 没有找到文件或读取文件失败")
        os._exit(0)

    new_data = origin_data[:, 0:3]
    for k in range(int((origin_data.shape[1] - 3) / 2)):
        new_data = np.row_stack((new_data, np.column_stack((origin_data[:, 0], origin_data[:, 2 * k + 3:2 * k + 5]))))

    start_time = new_data[:, 1].flatten()
    end_time = new_data[:, 2].flatten() + start_time
    port = new_data[:, 0].flatten()
    port_loop = len(port)
    time_dots = np.array(list(sorted(set(np.concatenate((end_time, start_time), axis=0)))))

    Statement_number = len(time_dots) - 1
    Port_number = 24

    time_interval = [time_dots[k + 1] - time_dots[k] for k in range(Statement_number)]
    time_interval = np.array(time_interval)
    time_sequence = np.zeros((Statement_number, Port_number + 2))
    time_sequence[:, -1] = time_interval
    time_sequence[:, 0] = time_dots[:-1] + 1

    # 通道处理
    for k in range(Statement_number):
        for n in range(port_loop):
            if time_sequence[k, 0] > start_time[n] and time_sequence[k, 0] < end_time[n]:
                time_sequence[k, int(port[n])] = 1

    index_of_final = list(np.where(end_time == max(end_time))[0])

    time_sequence = time_sequence[:, 1:]

    time_sequence_new = []
    for n in range(Statement_number):
        temp_list = [int(x) for x in time_sequence[n, :-1].tolist()]
        temp_list = [str(x) for x in temp_list]
        temp = hex(int(''.join(temp_list), 2))
        time_sequence_new.append([temp, time_sequence[n, -1]])

    return time_sequence_new


def data_write(filename, data):
    with open(filename, "w") as f:
        for item in data:
            # f.write(str(bin(int(item[0], 16)))+','+str(item[1])+'ns')
            f.write(item[0] + ',' + str(item[1]) + 'ns')
            f.write('\n')


# origin_time_data = 'loop.xlsx'
#
# time_sequence = data_trans(origin_time_data)
# data_write('loop.pb', time_sequence)
# print(time_sequence)





