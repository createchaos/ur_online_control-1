'''
Created on 11.10.2017

@author: rustr
'''
from __future__ import print_function

import ur_online_control.control_core.global_access as global_access
import time

class ClientWrapper(object):
    
    def __init__(self, identifier):
        self.identifier = identifier
        self.connected = False
        self.snd_queue = None
        self.rcv_queues = None
    
    def wait_for_connected(self):
        print("Waiting until client %s is connected..." % self.identifier)
        connected_clients = global_access.CONNECTED_CLIENTS.keys()
        while self.identifier not in connected_clients:
            time.sleep(0.1)
            connected_clients = global_access.CONNECTED_CLIENTS.keys()
        print("Client %s is connected." % self.identifier)
        self.connected = True
        self.rcv_queues = global_access.RCV_QUEUES.get(self.identifier)
        self.snd_queue = global_access.SND_QUEUES.get(self.identifier)
         
    def wait_for_message(self, msg_id):
        if not self.connected:
            print("Client %s is NOT yet connected." % self.identifier)
            return
        
        self.rcv_queues[]
        
        while self.rcv_queue.empty():
            time.sleep(0.1)
            print("Waiting..")
        msg = self.rcv_queue.get(block = True)
        return msg
    