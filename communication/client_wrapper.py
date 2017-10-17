'''
Created on 11.10.2017

@author: rustr
'''
from __future__ import print_function

import global_access
from msg_identifiers import *
import time
from ur_online_control.communication.states import *

msg_identifier_names = {v: k for k, v in msg_identifier_dict.iteritems()}

class ClientWrapper(object):
    
    def __init__(self, identifier):
        self.identifier = identifier
        self.connected = False
        self.snd_queue = None
        self.rcv_queues = None
        
        self.waiting_time_queue = 0.1
    
    def wait_for_connected(self):
        print("Waiting until client %s is connected..." % self.identifier)
        connected_clients = global_access.CONNECTED_CLIENTS.keys()
        while self.identifier not in connected_clients:
            time.sleep(0.1)
            connected_clients = global_access.CONNECTED_CLIENTS.keys()
        print("Client %s is connected." % self.identifier)
        self.connected = True
        self.snd_queue = global_access.SND_QUEUE.get(self.identifier)
        self.rcv_queues = global_access.RCV_QUEUES.get(self.identifier)
        """
        
        for msg_id in self.rcv_queues:
            print("msg_id", msg_id)
            msg_id_name = msg_identifier_dict_inv[msg_id] 
            print("msg_id_name", msg_id_name)
            exec("self.%s_queue = " % msg_id_name[4:].lower())
            print("key", key)
        """
        
         
    def wait_for_message(self, msg_id):
        if not self.connected:
            print("Client %s is NOT yet connected." % self.identifier)
            return
        if msg_id not in self.rcv_queues:
            print("Client %s does NOT send messages of type %s." % (self.identifier, msg_identifier_names[msg_id]))
            return
        
        print("Waiting for message %s from %s" % (msg_identifier_names[msg_id], self.identifier))
        msg = self.rcv_queues[msg_id].get(block = True)
        return msg
    
    def wait_for_float_list(self):
        return self.wait_for_message(MSG_FLOAT_LIST)
    
    def wait_for_int(self):
        # still needs to be implemented
        return self.wait_for_message(MSG_INT)
    
    def wait_for_ready(self):
        state = global_access.CONNECTED_CLIENTS.get(self.identifier)
        while state != READY_TO_PROGRAM:
            time.sleep(0.1)
            state = global_access.CONNECTED_CLIENTS.get(self.identifier)
        return state
    
    def send(self, msg_id, msg):
        global_access.CONNECTED_CLIENTS.put(self.identifier, EXECUTING)
        self.snd_queue.put((msg_id, msg))
    
    def send_float_list(self, msg):
        self.send(MSG_FLOAT_LIST, msg)
    
    def send_command(self, cmd_id, msg):
        self.send(MSG_COMMAND, (cmd_id, msg))
    
    def send_command_movel(self, msg):
        self.send_command(COMMAND_ID_MOVEL, msg)
    
    def send_command_movej(self, msg):
        self.send_command(COMMAND_ID_MOVEJ, msg)
    
    def send_command_digital_out(self, msg):
        self.send_command(COMMAND_ID_DIGITAL_OUT, msg)
        
    
    
    
    
    
    
    