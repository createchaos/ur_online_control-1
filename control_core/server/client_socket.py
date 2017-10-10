'''
Created on 02.12.2013

@author: rustr
'''

from globals import *
import globals

from threading import Thread
import struct
from Queue import Queue
import socket
import time
import sys

#===============================================================================
# Client Socket
#===============================================================================
class ClientSocket(Thread):
    """ The Client Socket is the base for the specific client sockets 
    It can be used for both Receiver and Sender Sockets. """
    
    def __init__(self, socket, parent, identifier, **params):
        Thread.__init__(self)
        self.daemon = True
                
        self.socket = socket
        self.identifier = identifier
        self.parent = parent
        
        self.socket_type = None
        
        self.msg_rcv = ""
        self.byteorder = "!" # "!" network, ">" big-endian, "<" for little-endian, see http://docs.python.org/2/library/struct.html
        
        self.running = True
        
        "Edit romana: 03.06.2014"
        self.time_stamp_of_received_message = 0
        
        if 'sender' in params:
            if params['sender'] == True:
                self.run = self._run_as_sender
                self.socket_type = "SND"
                
        
        if 'receiver' in params:
            if params['receiver'] == True:
                self.run = self._run_as_receiver
                self.socket_type = "RCV"
        
        if 'socket_lock' in params:
            if params['socket_lock'] == True:
                self._send = self._send_with_socket_lock
                self._read = self._read_with_socket_lock
                self.socket.settimeout(0.008)
                #pass
        
        "Edit romana: 28.08.2016"
        if "ip" in params:
            self.ip = params["ip"]
                
                
                # self.socket_type = "SND_RCV" # should be RCV or SND
        
        print ":::::::::created %s Socket as %s." % (identifier, "sender" if "sender" in params else "receiver")
        
        self.logging = False
                                                
    #===========================================================================
    def close(self):
        self.running = False
        self.socket.close()
        "TODO: how to close thread ??"
        print "%sSocket %s: closed." % (self.identifier, self.socket_type)
    #===========================================================================
    def set_stack_counter(self, num):
        self.parent.set_stack_counter(num)
    #===========================================================================
    def get_stack_counter(self):
        return self.parent.get_stack_counter()
    #===========================================================================
    def set_waypoint_counter(self, num):
        self.parent.set_waypoint_counter(num)
    #===========================================================================
    def publish_waypoint_counter_executed(self, msg_counter):
        self.parent.publish_waypoint_counter_executed(msg_counter)
    #===========================================================================
    def get_waypoint_counter(self):
        return self.parent.get_waypoint_counter()
    #===========================================================================
    def publish_state(self, state):
        self.parent.publish_state(state)
    #===========================================================================
    def _read(self):
        """ The transmission protocol for messages is 
        [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier] """
        
        "This is called if bytes are available, so store the time stamp."
        self.time_stamp_of_received_message = time.time()
        
        "1. read msg length"
        self.msg_rcv += self.socket.recv(4)
        if len(self.msg_rcv) < 4:
            return
        msg_length = struct.unpack_from(self.byteorder + "i", self.msg_rcv, 0)[0]
        
        "2. read msg according to msg_length"        
        self.msg_rcv += self.socket.recv(msg_length)
        if len(self.msg_rcv) < (msg_length + 4):
            return
        
        "3. message identifier"
        msg_id = struct.unpack_from(self.byteorder + "i", self.msg_rcv[4:8], 0)[0]
        
        "4. rest of message, according to msg_length"
        raw_msg = self.msg_rcv[8:(8 + msg_length - 4)]
        
        "5. set self.msg_rcv to the rest"
        self.msg_rcv = self.msg_rcv[(8 + msg_length - 4):]
        
        "4. pass message id and raw message to process method "
        self.process(msg_length, msg_id, raw_msg, self.time_stamp_of_received_message)
        
    #===========================================================================
    def _read_with_socket_lock(self):
        
        """ The transmission protocol for messages is 
        [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier] """
        
        "This is called if bytes are available, so store the time stamp."
        # self.time_stamp_of_received_message = round(time.time() * 1000)
        self.time_stamp_of_received_message = time.time()
                
        self.parent.socket_lock.acquire()
        try:
            self.msg_rcv += self.socket.recv(4)
        except socket.timeout:
            self.parent.socket_lock.release()
            return
            
        if len(self.msg_rcv) < 4:
            self.parent.socket_lock.release()
            return
        
        "1. read msg length"
        msg_length = struct.unpack_from(self.byteorder + "i", self.msg_rcv, 0)[0]
        
        #print "msg_length", msg_length
        
        "2. read msg according to msg_length"        
        try:
            self.msg_rcv += self.socket.recv(msg_length)
        except socket.timeout:
            self.parent.socket_lock.release()
            return
        self.parent.socket_lock.release()
        
        if len(self.msg_rcv) < (msg_length + 4):
            return
        
        "3. message identifier"
        msg_id = struct.unpack_from(self.byteorder + "i", self.msg_rcv[4:8], 0)[0]

        
        #print "%sSocket: msg_id %d" % (self.identifier, msg_id)
        
        "4. rest of message, according to msg_length"
        raw_msg = self.msg_rcv[8:(8 + msg_length - 4)]
        "5. set self.msg_rcv to the rest"
        self.msg_rcv = self.msg_rcv[(8 + msg_length - 4):]
        
        #print "raw_msg", raw_msg
        
        if self.logging == True:
            print "msg_id", msg_id
            print "len(raw_msg)", len(raw_msg)
            print "%d %d %s\n" % (msg_length, msg_id, struct.unpack_from("!" + "%ii" % (int(len(raw_msg)/4)), raw_msg))
            print "len(self.msg_rcv)", len(self.msg_rcv)
        
        
        #print "msg_length, msg_id, raw_msg", msg_length, msg_id, raw_msg
        
        "6. pass message id and raw message to process method "
        self.process(msg_length, msg_id, raw_msg, self.time_stamp_of_received_message)
    
    #===========================================================================
    def read(self):
        try:
            self._read()
        except socket.error as e:
            if e.errno == socket.errno.WSAECONNRESET: # An existing connection was forcibly closed by the remote host
                print "%sClient %s is not available anymore." % (self.identifier, self.socket_type)
                self.parent.close()
                pass
            else:
                print sys.exc_info()
                raise
    #===========================================================================
    def process(self, msg_len, msg_id, raw_msg, time_stamp = None):
        """ The transmission protocol for messages is 
        [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier]
            
            identifiers of receive messages:
            MSG_COMMAND_RECEIVED = 4 # [index]
            MSG_CURRENT_POSE_CARTESIAN = 5 # [position, orientation]
            MSG_CURRENT_POSE_JOINT = 6 # [j1, j2, j3, j4, j5, j6]
            MSG_STRING = 7 # [string] 
            MSG_FLOAT_ARRAY = 8 # [float, float, ...] """
                   
        if msg_id == MSG_COMMAND_RECEIVED:
            msg_counter = struct.unpack_from(self.byteorder + "i", raw_msg)[0]
            self.process_msg_cmd_received(msg_counter)
        
        elif msg_id == MSG_COMMAND_EXECUTED:
            "Actuators send the waypoint counter together with the msg_id, other Clients just the msg_id."
            if len(raw_msg):
                msg_counter = struct.unpack_from(self.byteorder + "i", raw_msg)[0]
            else:
                msg_counter = None
            self.process_msg_cmd_executed(msg_counter)
        
        elif msg_id == MSG_ACTUATOR_INIT:
            self.process_actuator_init(raw_msg)
            
        elif msg_id == MSG_CURRENT_POSE_CARTESIAN:
            msg_current_pose_cartesian = self.get_current_pose_cartesian(raw_msg)
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_current_pose_cartesian, time_stamp, wait = True) 
        
        elif msg_id == MSG_CURRENT_POSE_JOINT:
            msg_current_pose_joint = self.get_current_pose_joint(raw_msg)
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_current_pose_joint, time_stamp, wait = True)   
                        
        elif msg_id == MSG_ANALOG_IN:
            msg_analog_in = self.get_analog_in(raw_msg)
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_analog_in, time_stamp, wait = True)
        
        elif msg_id == MSG_STRING:
            msg_string = struct.unpack_from(self.byteorder + str(msg_len-4) + "s", raw_msg)[0]
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_string, time_stamp, wait = True)    
                    
        elif msg_id == MSG_FLOAT_LIST: 
            msg_float_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "f", raw_msg)
            msg_float_list = [item for item in msg_float_tuple]
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_float_list, time_stamp, wait = True)
            
        elif msg_id == MSG_COMMAND: 
            msg_float_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "f", raw_msg)
            msg_float_list = [item for item in msg_float_tuple]
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_float_list, time_stamp, wait = True)
            
        else:
            print "%sSocket: msg_id %d" % (self.identifier, msg_id)
            print "%sSocket: Message identifier unknown:  %s = %d, message: %s" % (self.identifier, msg_identifier_str_array[msg_id], msg_id, raw_msg)
            return   
    
    #=====================================================================
    def send(self, msg_id, msg = None):
        """ The transmission protocol for send messages is 
        [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier]
        """
        buf = None
        
        if msg_id == MSG_COMMAND:
            " will be overwritten by the individual client sockets > send_command"
            self.send_command(msg)
            return
        if msg_id == MSG_SPEED: # Romana edit 04.03.2014
            " will be overwritten by the individual client sockets > send_speed"
            self.send_speed(msg)
            return
        elif msg_id == MSG_QUIT:
            msg_snd_len = 4
            params = [msg_snd_len, msg_id]
            buf = struct.pack(self.byteorder + "2i", *params)
            
        elif msg_id == MSG_STOP: # Romana edit 14.07.2015
            self.send_stop()
            return
            
        elif msg_id == MSG_STRING or msg_id == MSG_OPERATION:
            msg_snd_len = len(msg) + 4                
            params = [msg_snd_len, msg_id, msg]
            buf = struct.pack(self.byteorder + "2i" + str(len(msg)) +  "s", *params)
        elif msg_id == MSG_FLOAT_LIST:
            msg_snd_len = struct.calcsize(str(len(msg)) + "f") + 4
            msg = [item for item in msg] # change tuple to list
            params = [msg_snd_len, msg_id] + msg
            buf = struct.pack(self.byteorder + "2i" + str(len(msg)) +  "f", *params)
        
        elif msg_id == MSG_DOUBLE_LIST:
            msg_snd_len = struct.calcsize(str(len(msg)) + "d") + 4
            msg = [item for item in msg] # change tuple to list
            params = [msg_snd_len, msg_id] + msg
            buf = struct.pack(self.byteorder + "2i" + str(len(msg)) +  "d", *params)
            
        else:
            print "%sSocket: Message identifier unknown:  %s = %d, message: %s" % (self.identifier, msg_identifier_str_array[msg_id], msg_id, msg)
            return   
        
        self._send(buf)
        #print "%sSocket: Sent message: %s." % (self.identifier, msg_identifier_str_array[msg_id])
    #===========================================================================
    def _send_with_socket_lock(self, buf):
        
        self.parent.socket_lock.acquire()
        self.socket.send(buf)
        self.parent.socket_lock.release()
    #===========================================================================
    def _send(self, buf):  
        self.socket.send(buf)
    #===========================================================================      
    def send_command(self, msg):
        """ will be overwritten by the individual client sockets """
        pass
    #===========================================================================
    def process_msg_cmd_received(self, msg_counter):
        """ will be overwritten by the individual client sockets """
        pass
    #===========================================================================
    def process_msg_cmd_executed(self, msg_counter=None):
        """ will be overwritten by the individual client sockets """
        pass
    #===========================================================================     
    def process_actuator_init(self, raw_msg):
        """ will be overwritten by the individual client sockets """
        pass
    #===========================================================================
    def get_current_pose_cartesian(self, raw_msg):
        """ will be overwritten by the individual client sockets """
        return
    #===========================================================================
    def get_current_pose_joint(self, raw_msg):
        """ MSG_CURRENT_POSE_JOINT = 6 # [j1, j2, j3, j4, j5, j6] """
        return
    #===========================================================================
    def get_analog_in(self, raw_msg):
        return
    #=========================================================================== 
    def run(self):
        "needs to be overwritten"
        # self.run_as_receiver()
        pass
    #=========================================================================== 
    def _run_as_sender(self):
        dQ = globals.SEND_QUEUES.get(self.identifier)
        dQI = globals.INTERRUPT_QUEUES.get(self.identifier)
        while self.running:
            # first process all interrupts
            while not dQI.empty():
                
                msg_id, msg = dQI.get()
                #print "dQI", msg_identifier_str_array[msg_id]
                try:
                    self.send(msg_id, msg)
                except socket.error as e:
                    if e.errno == 10054 or e.errno == 10053:
                        print "%s: Client has been disconnected." % (self.identifier)
                        self.parent.close()
                    else:
                        raise e
            
            if not dQ.empty():
                msg_id, msg = dQ.get()
                #print "data q", msg_id, msg, dQ.length()
                try:
                    self.send(msg_id, msg)
                except socket.error as e:
                    if e.errno == 10054 or e.errno == 10053:
                        print "%s: Client has been disconnected." % (self.identifier)
                        self.parent.close()
                    else:
                        raise e
        self.close()
    #===========================================================================
    def _run_as_receiver(self):
        while self.running:
            try:
                self.read() 
            except socket.error as e:
                if e.errno == 10054 or e.errno == 10053:
                    print "%s: Client has been disconnected." % (self.identifier)
                    self.parent.close()
                else:
                    raise e
        self.close()
#===============================================================================

if __name__ == "__main__":
    print  msg_identifier_str_array[10]