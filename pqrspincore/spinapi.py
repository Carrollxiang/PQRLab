import ctypes

import re

import pqrspincore.DecodeSignal as ds


PULSE_PROGRAM = 0
FREQ_REGS = 1

try:
    spinapi = ctypes.CDLL("spinapi64")
except:
    try:
        spinapi = ctypes.CDLL("spinapi")
    except:
        print("Failed to load spinapi library.")
        pass


def enum(**enums):
    return type('Enum', (), enums)


ns = 1.0
us = 1000.0
ms = 1000000.0

unit_list = {
    'ns': 1.0,
    'us': 1000.0,
    'ms': 1000000.0
}

MHz = 1.0
kHz = 0.001
Hz = 0.000001

#   Instruction enum
Inst = enum(
    CONTINUE = 0,
    STOP = 1,
    LOOP = 2,
    END_LOOP = 3,
    JSR = 4,
    RTS = 5,
    BRANCH = 6,
    LONG_DELAY = 7,
    WAIT = 8,
    RTI = 9
)

inst_dict = {
    "CONTINUE": "0",
    "STOP": "1",
    "LOOP": "2",
    "END_LOOP": "3",
    "JSR": "4",
    "RTS": "5",
    "BRANCH": "6",
    "LONG_DELAY": "7",
    "WAIT": "8",
    "RTI": "9"
}

inst_list = [
    "CONTINUE",
    "STOP",
    "LOOP",
    "END_LOOP",
    "JSR",
    "RTS",
    "BRANCH",
    "LONG_DELAY",
    "WAIT",
    "RTI"
]


channel_list = {
    '0': 'scmos',
    '1': '780cooling',
    '2': '780repump',
    '3': 'EOM_ttl',
    '4': '795depump_back',
    '5': '795depump_front',
    '6': '795repump',
    '7': '795state_prepare',
    '8': '780probe_space_AOM',
    '9': 'reset',
    '10': 'single_photon_AOM',
    '11': 'v_dipole',
    '12': '480detune',
    '13': '480readout',
    '14': 'qutau_trigger',
    '15': '780probe_fiber_AOM',
    '16': 'spd_gate',
    '17': 'spd_gate',
    '18': 'spd_gate',
    '19': 'spd_gate',
    '20': 'unused',
    '21': 'always_on',
    '22': 'always_on',
    '23': 'always_on',
}

spinapi.pb_get_version.restype = (ctypes.c_char_p)
spinapi.pb_get_error.restype = (ctypes.c_char_p)

spinapi.pb_count_boards.restype = (ctypes.c_int)

spinapi.pb_init.restype = (ctypes.c_int)

spinapi.pb_select_board.argtype = (ctypes.c_int)
spinapi.pb_select_board.restype = (ctypes.c_int)

spinapi.pb_set_debug.argtype = (ctypes.c_int)
spinapi.pb_set_debug.restype = (ctypes.c_int)

spinapi.pb_set_defaults.restype = (ctypes.c_int)

spinapi.pb_core_clock.argtype = (ctypes.c_double)
spinapi.pb_core_clock.restype = (ctypes.c_int)

spinapi.pb_write_register.argtype = (ctypes.c_int, ctypes.c_int)
spinapi.pb_write_register.restype = (ctypes.c_int)

spinapi.pb_start_programming.argtype = (ctypes.c_int)
spinapi.pb_start_programming.restype = (ctypes.c_int)

spinapi.pb_stop_programming.restype = (ctypes.c_int)

spinapi.pb_start.restype = (ctypes.c_int)
spinapi.pb_stop.restype = (ctypes.c_int)
spinapi.pb_reset.restype = (ctypes.c_int)
spinapi.pb_close.restype = (ctypes.c_int)

spinapi.pb_inst_dds2.argtype = (
    ctypes.c_int,   # Frequency register DDS0
    ctypes.c_int,   # Phase register DDS0
    ctypes.c_int,   # Amplitude register DDS0
    ctypes.c_int,   # Output enable DDS0
    ctypes.c_int,   # Phase reset DDS0
    ctypes.c_int,   # Frequency register DDS1
    ctypes.c_int,   # Phase register DDS1
    ctypes.c_int,   # Amplitude register DDS1
    ctypes.c_int,   # Output enable DDS1,
    ctypes.c_int,   # Phase reset DDS1,
    ctypes.c_int,   # Flags
    ctypes.c_int,   # inst
    ctypes.c_int,   # inst data
    ctypes.c_double,    # timing value (double)
)

spinapi.pb_inst_dds2.restype = (ctypes.c_int)

spinapi.pb_inst_pbonly.argtype = (
    ctypes.c_int,   # Flags
    ctypes.c_int,   # inst
    ctypes.c_int,   # inst data
    ctypes.c_double,    # timing value (double)
)

spinapi.pb_inst_pbonly.restype = (ctypes.c_int)




def pb_get_version():
    """Return library version as UTF-8 encoded string."""
    ret = spinapi.pb_get_version()
    return str(ctypes.c_char_p(ret).value.decode("utf-8"))


def pb_get_error():
    """Return library error as UTF-8 encoded string."""
    ret = spinapi.pb_get_error()
    return str(ctypes.c_char_p(ret).value.decode("utf-8"))


def pb_count_boards():
    """Return the number of boards detected in the system."""
    return spinapi.pb_count_boards()


def pb_init():
	"""Initialize currently selected board."""
	return spinapi.pb_init()


def pb_set_debug(debug):
	return spinapi.pb_set_debug(debug)


def pb_select_board(board_number):
	"""Select a specific board number"""
	return spinapi.pb_select_board(board_number)


def pb_set_defaults():
	"""Set board defaults. Must be called before using any other board functions."""
	return spinapi.pb_set_defaults()


def pb_core_clock(clock):
	return spinapi.pb_core_clock(ctypes.c_double(clock))


def pb_write_register(address, value):
	return spinapi.pb_write_register(address, value)


def pb_start_programming(target):
	return spinapi.pb_start_programming(target)


def pb_stop_programming():
	return spinapi.pb_stop_programming()


def pb_inst_dds2(*args):
	t = list(args)
	# Argument 13 must be a double
	t[13] = ctypes.c_double(t[13])
	args = tuple(t)
	return spinapi.pb_inst_dds2(*args)


def pb_inst_pbonly(*args):
    t = list(args)
    t[3] = ctypes.c_double(t[3])
    args = tuple(t)
    return spinapi.pb_inst_pbonly(*args)


def pb_multi_inst(construction_list):
    for construction in construction_list:
        pb_inst_pbonly(construction)


def pb_start():
    return spinapi.pb_start()


def pb_stop():
    return spinapi.pb_stop()


def pb_reset():
    return spinapi.pb_reset()


def pb_close():
    return spinapi.pb_close()


def pb_test(Flags, inst, inst_data, timing):
    t = [Flags, inst, inst_data, timing]
    print(type(t)) #  Argument 4 must be a double
    t[3] = ctypes.c_double(t[3])
    success = 'You did it'
    return success





def get_pb_data(line):
    label = re.findall(r"^[a-zA-z]+", line)
    if len(label) != 0:
        label = label[0]
    else:
        label = ''

    output_pattern = re.findall(r"0b[\w\s]+",re.findall(r"0b[\w\s]+\,", line)[0])[0].replace(' ', '')  # 2进制
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
    # print(unit)
    # comment = re.findall(r"//.*", line)
    return output_pattern, time, inst, inst_data, unit

def pb_initail():
    pbclock=300        # 时钟频率300MHz

    # Enable the log file
    pb_set_debug(0)    # 0表示不进入编程状态

    print("Using SpinAPI Library version %s" % pb_get_version())         # 获得当前API版本，目前是20171214
    print("Found %d boards in the system.\n" % pb_count_boards())        # 检测当前的板子数量！

    pb_select_board(0)      # 0为默认值，是第一块板子

    if pb_init() != 0:  # 板子初始化 模式正常则返回0
        raise Exception("Number: %d" % pb_count_boards())
        # raise Exception("Error initializing board: %s" % pb_get_error())
        # print("Error initializing board: %s" % pb_get_error())     #返回错误类型
        # # input("Please press a key to continue.")
        # exit(-1)

    # Configure the core clock
    pb_core_clock(pbclock)  # 时钟频率设置


def load_channels(AllSignals, input_type = 'LoopedSignal'):
    """

    :param AllSignals: [[Port_1,Signal_1,Delay_1]....[port_n,Signal_n,Delay_n]]
    :return:
    """
    sequence_list = []
    delay_list = [AllSignals[i][2] for i in range(len(AllSignals))]
    max_delay = max(delay_list)
    for index, channel in enumerate(AllSignals):
        temp = ds.decode_multi_loop(channel[1])
        temp = ds.adjust_general_delay(temp, channel[2], max_delay)
        # print(index, temp)
        sequence_list.append([channel[0], temp])

    channels_sequence = ds.synchronize_complex_sqeuence(sequence_list)
    pb_reset()
    pb_start_programming(PULSE_PROGRAM)
    for index, sequence in enumerate(channels_sequence):
        # exec('pb_inst_pbonly(bin(int(sequence[0])), int(sequence[2]), int(sequence[3]), sequence[1])'.format{bin(int(sequence[0])),int(sequence[2]),int(sequence[3]),sequence[1]})
        # print(str(bin(int(sequence[0]))) + "," + str(int(sequence[1])) + "ns," + str(int(sequence[2])) + "," + str(
        #     int(sequence[3])))
        # print('pb_inst_pbonly({}, {}, {}, {})'
        #      .format(bin(int(sequence[0])), int(sequence[2]), int(sequence[3]), sequence[1]))


        if int(sequence[2]) == 0:
            print(str(bin(int(sequence[0])))+","+str(int(sequence[1]))+"ns")
        elif int(sequence[3]) == 0:
            print(str(bin(int(sequence[0]))) + "," + str(int(sequence[1])) + "ns," + inst_list[int(sequence[2])])
        else:
            print(str(bin(int(sequence[0])))+","+str(int(sequence[1]))+"ns,"+inst_list[int(sequence[2])]+","+str(int(sequence[3])))
    # pb_inst_pbonly(0b111000000000000000000000, Inst.CONTINUE, 0, 200.0 * us)
    pb_stop_programming()

