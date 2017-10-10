'''
Created on 08.11.2013

@author: kathrind
'''

#===============================================================================
# MESSAGE IDENTIFIERS
#==============================================================================

""" Message Identifiers for sending and receiving messages from the clients
Message always consists of uint4: length of message, uint4: type of message, message (depends on the specific kind) """ 
MSG_COMMAND = 1 # [counter, position, orientation, optional values]
MSG_STOP = 2
MSG_QUIT = 3 
MSG_COMMAND_RECEIVED = 4 # [counter]
MSG_CURRENT_POSE_CARTESIAN = 5 # [position, orientation]
MSG_CURRENT_POSE_JOINT = 6 # [j1, j2, j3, j4, j5, j6]
MSG_STRING = 7 # [string]
MSG_FLOAT_LIST = 8 # [float, float, ...]
MSG_OPERATION = 9 # [string] (the name of the operation)
MSG_ACTUATOR_INIT = 10 # tool[position, orientation] + base[position, orientation]
MSG_ANALOG_IN = 11
MSG_ANALOG_OUT = 12
MSG_DIGITAL_IN = 13
MSG_DIGITAL_OUT = 14
MSG_COMMAND_EXECUTED = 15
MSG_IDENTIFIER = 16
MSG_CURRENT_SCAN = 17
MSG_FLOAT = 18
MSG_SPEED = 19 # current speed to modify
MSG_INT_LIST = 20 # [int, int, ...]
MSG_DOUBLE_LIST = 21 # [double, double, ...]
MSG_UR_DATA = 22 # [pose, analog in]
MSG_FORCE = 23
MSG_ANGLES = 24
MSG_CLEAR_BUFFER = 25 # for clearing the remote buffer of positions for the robot

# FOR THE MOVING BASE
MSG_MOVE_BASE = 26 # [float1, float2] float1: seconds to move, + = forward - = backward, float2: speed value
MSG_MOVE_BASE_TO_POS = 27 # [position, orientation, speed] = [x, y, z, q1, q2, q3, q4, s] (orientation as quaternion)

MSG_CARDAN_TOOL_DATA = 28 # [angleA, angleB, force]
MSG_VOLTAGE_CURRENT = 29 # [voltage, current]
MSG_CURRENT_SPEED = 30
MSG_TOOL_ANGLES = 31

MSG_PID_FORCE = 32


msg_identifier_str_array = ["0","MSG_COMMAND", "MSG_STOP", "MSG_QUIT", "MSG_COMMAND_RECEIVED", \
                            "MSG_CURRENT_POSE_CARTESIAN", "MSG_CURRENT_POSE_JOINT", "MSG_STRING", \
                            "MSG_FLOAT_LIST", "MSG_OPERATION","MSG_ACTUATOR_INIT", "MSG_ANALOG_IN", \
                            "MSG_ANALOG_OUT", "MSG_DIGITAL_IN", "MSG_DIGITAL_OUT", "MSG_COMMAND_EXECUTED", \
                            "MSG_IDENTIFIER", "MSG_CURRENT_SCAN", "MSG_FLOAT", "MSG_SPEED", "MSG_FLOAT_INT", \
                            "MSG_DOUBLE_LIST", "MSG_UR_DATA", "MSG_FORCE", "MSG_ANGLES", "MSG_CLEAR_BUFFER", \
                            "MSG_MOVE_BASE", "MSG_MOVE_BASE_TO_POS", "MSG_CARDAN_TOOL_DATA", "MSG_VOLTAGE_CURRENT", \
                            "MSG_CURRENT_SPEED", "MSG_TOOL_ANGLES", "MSG_PID_FORCE"]


