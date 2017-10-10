'''
Created on 29.11.2013

@author: rustr
'''


import globals
import time
from threading import Lock

#===============================================================================
class Base(object):
    def __init__(self, identifier):
        super(Base, self).__init__()
        self.identifier = identifier
        self.sender_ip = ""
        self.receiver_ip = ""
        print "CLIENT_OBJECTS: %s: INIT." % self.identifier
        self.state = globals.READY
        self.connected = True
        self.lock = Lock()
        "send queue"
        self.sndQ = globals.SEND_QUEUES.get(self.identifier)
        self.interruptQ = globals.INTERRUPT_QUEUES.get(self.identifier)
        
    
    def set_sender_ip(self, ip):
        self.lock.acquire()
        self.sender_ip = ip
        self.lock.release()
    
    def set_receiver_ip(self, ip):
        self.lock.acquire()
        self.receiver_ip = ip
        self.lock.release()
    
    def set_state(self, state):
        self.lock.acquire()
        self.state = state
        self.lock.release()
        
    def ready(self):
        return self.state == globals.READY
    
    def set_ready_state(self):
        self.set_state(globals.READY)
    
    def set_busy_state(self):
        self.set_state(globals.BUSY)

    def send(self, msg_id, msg = None):
        self.set_busy_state()
        self.sendQ.put((msg_id, msg))
    
    def send_double_list(self, msg):
        self.set_busy_state()
        self.sndQ.put((globals.MSG_DOUBLE_LIST, msg))
        
    def quit(self):        
        self.sndQ.put((globals.MSG_QUIT, None))
    
    def stop(self):
        self.interruptQ.clear()
        self.interruptQ.put((globals.MSG_STOP, None))
    
    def set_tool(self):
        "overwritten by other objects"
        pass 
    
    def wait_for_message(self, msg_id):
        dQ = self.get_data_queue(msg_id)
        while dQ.empty():
            time.sleep(globals.SMALL_VALUE)
        msg = dQ.get(wait=True)
        return msg

    def get_data_queue(self, msg_id):
        return globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
    
    def get_data_from_queue(self, msg_id, **params):
        dQ = self.get_data_queue(msg_id)
        return dQ.get(**params)
    
#===============================================================================


