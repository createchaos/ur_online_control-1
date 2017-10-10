'''
Created on 12.11.2013

@author: kathrind
'''

" Actuator States: "
READY_TO_PROGRAM = 1 # the buffer of the robot is empty, he is ready to receive commands (number = stacksize)
EXECUTING = 2 # the robot is executing the command
READY_TO_RECEIVE = 3 # the buffer of the robot has space, he is ready to receive the next command
COMMAND_EXECUTED = 6

" Client States: "
READY = 4
BUSY = 5

client_states_str_array = ["0","READY_TO_PROGRAM","EXECUTING","READY_TO_RECEIVE","READY","BUSY", "COMMAND_EXECUTED"]
