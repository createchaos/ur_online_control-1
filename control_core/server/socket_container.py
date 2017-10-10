'''
Created on 29.11.2013

@author: rustr
'''

from globals.client_states import READY
from globals.data_queues import DataQueue, DataLifoQueue
from globals.message_identifiers import *

import globals
from threading import Lock
import time

#===============================================================================
class SocketContainer(object):
    """Container for sender and receiver threads.
    Is connected to the client_object over SIGNALS.
    TODO: emitting signals to the object is possible receiving not yet. """
    
    def __init__(self, identifier, parent): # parent = Server
        super(SocketContainer, self).__init__()
        self.identifier = identifier
        self.parent = parent
        
        self.receiver = None
        self.sender = None
    
        self.receiver_connected = 0
        self.sender_connected = 0
        
        "TODO: see Server. how to know and handle if one disconnects?"
        
        "Used if both sender and receiver threads share the same socket."
        self.socket_lock = Lock()
        
        self.lock = Lock()
        
        self.state = READY
        
        "The following is just used by ActuatorSockets:"
        "The counter for the number of commands sent to the robot, reaches from -self.stack_size to 0."
        self.stack_counter = 0
        "The counter for the number of positions sent to the robot, starts with 0 up to endless."
        self.waypoint_counter = 0
        
        "TODO: the following should be put into the individual client sockets: they know what they need"
        #globals.RECEIVE_QUEUES.append(DataQueue(single_item=True), self.identifier, MSG_CURRENT_POSE_CARTESIAN)
        #globals.RECEIVE_QUEUES.append(DataLifoQueue(single_item=True), self.identifier, MSG_CURRENT_POSE_CARTESIAN)
        globals.RECEIVE_QUEUES.append(DataLifoQueue(), self.identifier, MSG_CURRENT_POSE_CARTESIAN)
        globals.RECEIVE_QUEUES.append(DataQueue(single_item=True), self.identifier, MSG_CURRENT_POSE_JOINT)
        globals.RECEIVE_QUEUES.append(DataQueue(single_item=True), self.identifier, MSG_CURRENT_SCAN)
        globals.RECEIVE_QUEUES.append(DataQueue(), self.identifier, MSG_COMMAND)
        
        globals.RECEIVE_QUEUES.append(DataQueue(single_item=True), self.identifier, MSG_ANALOG_IN)
        globals.RECEIVE_QUEUES.append(DataQueue(single_item=True), self.identifier, MSG_UR_DATA)
        globals.RECEIVE_QUEUES.append(DataQueue(), self.identifier, MSG_STRING)
        globals.RECEIVE_QUEUES.append(DataQueue(), self.identifier, MSG_FLOAT_LIST)
        globals.RECEIVE_QUEUES.append(DataQueue(single_item=True), self.identifier, MSG_INT_LIST)
        
        globals.RECEIVE_QUEUES.append(DataLifoQueue(), self.identifier, MSG_CURRENT_SPEED)
        
        
        globals.SEND_QUEUES.append(DataQueue(), self.identifier)
        globals.INTERRUPT_QUEUES.append(DataQueue(), self.identifier)
        
        "This is creating the client object with its identifier."
        globals.CLIENT_OBJECTS.append(self.identifier)
        
        self.client_object = globals.CLIENT_OBJECTS.get(self.identifier)
    
    def update_client_obj(self):
        obj = globals.CLIENT_OBJECTS.get(self.identifier)
        obj.set_state(self.state)
                
    def set_sender(self, sender):
        self.sender = sender
        self.sender.start()
        self.sender_connected = 1
        ip, port = sender.socket.getpeername()
        self.client_object.set_sender_ip(ip)
                
    def set_receiver(self, receiver, socket_lock = False):
        self.receiver = receiver
        self.receiver.start()
        self.receiver_connected = 1
        ip, port = receiver.socket.getpeername()
        self.client_object.set_receiver_ip(ip)
    
    def handle_stack(self):
        "Just used by ActuatorSockets."
        self.sender.handle_stack()
            
    def publish_state(self, state):
        "Called by self.sender and self.receiver."
        self.lock.acquire()
        self.state = state
        self.lock.release()
        self.update_client_obj()
       
    def process_actuator_init(self, current_pose_cartesian_tuple):
        obj = globals.CLIENT_OBJECTS.get(self.identifier)
        obj.set_tool(current_pose_cartesian_tuple)
    
    def close(self):
        print "SocketContainer close."
        # if self.sender: self.sender.close()
        # if self.receiver: self.receiver.close()
        self.parent.remove_client(self)
        
        
    def set_stack_counter(self, num):
        #print "SocketContainer set_stack_counter", self.stack_counter + num
        self.lock.acquire()
        self.stack_counter += num
        self.lock.release()
    
    def get_stack_counter(self):
        self.lock.acquire()
        sc = self.stack_counter
        self.lock.release()
        return sc
    
    def set_waypoint_counter(self, num):
        self.lock.acquire()
        self.waypoint_counter += num
        self.lock.release()
    
    def get_waypoint_counter(self):
        self.lock.acquire()
        wc = self.waypoint_counter
        self.lock.release()
        return wc
    
    def publish_waypoint_counter_executed(self, msg_counter):
        
        obj = globals.CLIENT_OBJECTS.get(self.identifier)
        obj.set_waypoint_counter_executed(msg_counter)
        
        
        
        
        
        
        
        
        
        
        
        
        
        