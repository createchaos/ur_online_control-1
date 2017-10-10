'''
Created on 22.11.2016

@author: rustr
'''

msg_identifier_dict = {'MSG_IDENTIFIER': 1, 
                       'MSG_COMMAND': 2, # [command_id, counter, position, orientation, optional values]
                       'MSG_COMMAND_RECEIVED': 3, 
                       'MSG_COMMAND_EXECUTED': 4, 
                       'MSG_CURRENT_POSE_CARTESIAN': 5, # [position, orientation]
                       'MSG_CURRENT_POSE_JOINT': 6, # [j1, j2, j3, j4, j5, j6]
                       'MSG_CURRENT_DIGITAL_IN': 7,  # get a list of xx digital in number, values
                       'MSG_ANALOG_IN': 8, 
                       'MSG_ANALOG_OUT': 9, 
                       'MSG_DIGITAL_IN': 10,
                       'MSG_DIGITAL_OUT': 11, 
                       'MSG_SPEED': 12, # set a global speed var 0 - 1
                       'MSG_INT_LIST': 13, 
                       'MSG_FLOAT_LIST': 14, 
                       'MSG_STRING': 15, 
                       'MSG_QUIT': 16 # terminates the program
                       }

# different command identifiers are sent after msg_id MSG_COMMAND
command_identifier_dict = {'COMMAND_ID_MOVEL': 1, 
                           'COMMAND_ID_MOVEJ': 2,
                           'COMMAND_ID_DIGITAL_OUT': 3}


for key, value in msg_identifier_dict.iteritems():
    exec("%s = %i" % (key, value))

for key, value in command_identifier_dict.iteritems():
    exec("%s = %i" % (key, value))