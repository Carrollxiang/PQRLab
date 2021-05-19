from spinapi import *


import numpy as np



# Enable the log file
pb_set_debug(1)

print("****************************************************")
print("Using SpinAPI Library version %s" % pb_get_version())
print("Found %d boards in the system.\n" % pb_count_boards())


pb_select_board(1)

if pb_init() != 0:
    print("Error initializing board: %s" % pb_get_error())
    input("Please press a key to continue.")
    exit(-1)

# Configure the core clock
pb_core_clock(150.0)

data_filename = '780.csv'
time_sequence = data_trans(data_filename)

# Program the pulse program
pb_start_programming(PULSE_PROGRAM)

# with open('command_line.txt', 'r+', encoding='UTF-8') as file:
#     for line in file:
#         exec(line)
"pb_inst_pbonly(0xffffff, 0, 0, 2000.0 * ms)"
# --------执行文本语句-----------
# exec('print(5)')
# exec("""for i in range(5):
#       print("iter time: %d" % i)""")
with open('300ns.pb', 'r+', encoding='UTF-8') as file:
    for line in file:
        if len(line.strip()) != 0:
            exec(get_pb_data(line))

# pb_inst_pbonly(0b1110 0000 0000 1000 0000 0000,END_LOOP,0,5*us) # //comment4
'''for k in range(2):
    pb_inst_pbonly(0xffffff, 0, 0, 2000.0 * ms)

    pb_inst_pbonly(0x000000, 0, 0, 2000.0 * ms)

    pb_inst_pbonly(0xffffff, 0, 0, 2000.0 * ms)
    # pb_inst_pbonly(time_sequence[0][0], Inst.LOOP, 500, time_sequence[0][1]*ns)
    pb_inst_pbonly(0x000000, 0, 0, 2000.0 * ms)'''


'''for item in time_sequence:
    pb_inst_pbonly(item[0], Inst.CONTINUE, 0, item[1]*ns)
    print(item)'''

pb_stop_programming()

# Trigger the board
pb_start()

input("Please press a key to stop.")

pb_stop()

pb_close()


