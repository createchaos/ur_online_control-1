'''
Created on 20.11.2013

@author: kathrind
'''

from client_socket import ClientSocket
import struct
from globals import *
import time
from threading import Lock
import math 
import socket
import globals
#===============================================================================
# Actuator Socket
#===============================================================================
class ActuatorSocket(ClientSocket):
    """ The ActuatorSocket extends, respectively differs from the ClientSocket 
    in a few points:
    1. The actuator can just handle a specific size of commands at once, so it 
       must be set in packets to a specific length ( = stack_size)
    2. The actuator can be in different states: READY_TO_PROGRAM, EXECUTING and 
       READY_TO_RECEIVE.
    3. If the ActuatorSocket has sent all messages on the stack, and also received 
       the same amount of messages, it will go into READY_TO_PROGRAM state. 
    """
    
    def __init__(self, socket, parent, identifier, **params):
        ClientSocket.__init__(self, socket, parent, identifier, **params)
        
        " array of commands from the operation which need to be sent to the Actuator"
        self.stack = []
        " Maximum of messages that the actuator can evaluate at once. "
        self.stack_size = 3
        
        " at the beginning, the state is set to zero, different states: READY_TO_PROGRAM = 1, EXECUTING = 2 and READY_TO_RECEIVE = 3 "
        self.publish_state(EXECUTING)
        
        self.byteorder = "<" # "!" network, ">" big-endian, "<" for little-endian, see http://docs.python.org/2/library/struct.html
        
    #=====================================================================        
    def send_command(self, msg):
        """ puts the send msg on the stack and calls handle_stack """
        self.stack.append(msg)
        self.handle_stack()
    #===================================================================== 
    def _send_command(self, cmd):
        """ will be overwritten by the individual client sockets
            called from handle stack: individual commands have to created for the specific actuator socket.
        """
        pass
    #===================================================================== 
    def send_speed(self, speed):
        print "%sSocket: method send_speed not yet implemented." % (self.identifier)
    #===================================================================== 
    def process_msg_cmd_received(self, msg_counter):
        """ count waypoints which are send back by the Actuator and publish according state """
        self.publish_state(READY_TO_RECEIVE)
        self.set_stack_counter(+1)
        "Parent will tell the sender socket to handle the stack"    
        self.parent.handle_stack()
        #print "%sSocket: process_msg_cmd_received, msg_counter %d." % (self.identifier, msg_counter)
    #===================================================================== 
    def process_msg_cmd_executed(self, msg_counter=None):
        """ will be overwritten by the individual client sockets """
    #=====================================================================
    def handle_specific_case(self):
        "This will be just a specific case until all actuators can send a proper MSG_EXECUTED."
        self.publish_state(READY_TO_PROGRAM)
    #=====================================================================
    def handle_stack(self):
        if not len(self.stack) and self.get_stack_counter() == 0: 
            " The actuator is ready to be programmed , different when receiving msg_cmd_executed: see UR."
            self.handle_specific_case()
        elif len(self.stack) and self.get_stack_counter() == 0 :
            " The actuator is ready to be programmed, and receives first packet from the stack "
            #print "%sSocket: The actuator needs to accomplish %i step%s in total." % (self.identifier, len(self.stack), "s" if len(self.stack) > 1 else "")
            for i in range(min(self.stack_size, len(self.stack))):
                cmd = self.stack.pop(0)
                self.set_waypoint_counter(+1)
                self.publish_state(EXECUTING)
                self._send_command(cmd)
                self.set_stack_counter(-1)
        elif len(self.stack) and -self.stack_size <= self.get_stack_counter() < 0 :
            " The actuator is currently executing, but ready to receive another packet from the stack "
            #print "%sSocket: The actuator needs to accomplish %i step%s in total." % (self.identifier, len(self.stack), "s" if len(self.stack) > 1 else "")
            # HACK !!!!!!
            # I don't know why this happens: comes here although len stack == 0, probably thread unsafe?
            try:
                #print "%sSocket: len(self.stack) %i." % (self.identifier, len(self.stack))
                cmd = self.stack.pop(0)
                self.set_waypoint_counter(+1)            
                self.publish_state(EXECUTING)
                self._send_command(cmd)
                self.set_stack_counter(-1)
            except IndexError:
                print "%sSocket: HACK!"  % self.identifier
        else: # len(self.stack) == 0 and self.stack_counter < 0
            " The actuator must still accomplish some commands and return them "
            #print "%sSocket: The actuator has still %d step%s to accomplish." % (self.identifier, len(self.stack) + self.get_stack_counter() * -1, "s" if len(self.stack) > 1 else "")            
            pass
            
        
    #===========================================================================
    def process_actuator_init(self, raw_msg):
        """ MSG_ACTUATOR_INIT: [position, orientation] """
        current_pose_cartesian_tuple = self.get_current_pose_cartesian(raw_msg)
        self.parent.process_actuator_init(current_pose_cartesian_tuple)
        self.publish_state(READY_TO_PROGRAM)
    #===========================================================================
    def get_current_pose_cartesian(self, raw_msg):
        """ will be overwritten by the individual client sockets """
        pass
    #===========================================================================
    def get_current_pose_joint(self, raw_msg):
        """ MSG_CURRENT_POSE_JOINT = 5 # [j1, j2, j3, j4, j5, j6] """
        pass
    
#===============================================================================
# ABB Socket
#===============================================================================
class ABBSocket(ActuatorSocket):
    
    def __init__(self, socket, parent, identifier, **params):
        ActuatorSocket.__init__(self, socket, parent, identifier, **params)  
        self.stack_size = 8
        self.msg_command_length = 48
    #===================================================================== 
    def _send_command(self, cmd):
        """ MSG_COMMAND = 1 # [counter, position, orientation, optional values]
            called from handle stack: individual commands have to created for the specific actuator socket.
            ABB: [x, y, z, q1, q2, q3, q4, int1, int2, int3]
        """
        
        # change order of quaternion ====
        x, y, z, q1, q2, q3, q4, int1, int2, int3 = cmd
        cmd = [x, y, z, q4, q1, q2, q3, int1, int2, int3]
        # ====
         
        params = [self.msg_command_length, MSG_COMMAND, self.get_waypoint_counter()] + cmd
        buf = struct.pack(self.byteorder + "3i7f3i", *params)
        self._send(buf)
        print "%sSocket: Sent pose with waypoint counter: %i." % (self.identifier, self.get_waypoint_counter()) 
        
        
    #=====================================================================        
    def get_current_pose_cartesian(self, raw_msg):
        """ MSG_CURRENT_POSE_CARTESIAN = 5 # [x, y, z, q1, q2, q3, q4] """
        current_pose_cartesian_tuple = struct.unpack_from(self.byteorder + "7f", raw_msg)   
        
        # change order of quaternion ====
        x, y, z, q1, q2, q3, q4 = current_pose_cartesian_tuple
        current_pose_cartesian_tuple = (x, y, z, q4, q1, q2, q3)
        # ====
        
        
        
        return current_pose_cartesian_tuple
    #===========================================================================
    def get_current_pose_joint(self, raw_msg):
        """ MSG_CURRENT_POSE_JOINT = 5 # [j1, j2, j3, j4, j5, j6] """
        pass
    
    #=====================================================================
    def handle_specific_case(self):
        return
    
    #===================================================================== 
    def process_msg_cmd_executed(self, msg_counter):
        print "ABBSocket: process message command executed", msg_counter
        if not len(self.stack) and self.get_stack_counter() == 0 and self.get_waypoint_counter() == msg_counter:
            self.publish_state(READY_TO_PROGRAM)


#===============================================================================
"""This are used to synchronize one clients waypoint counter to the other, so that
one waits until they have the same waypoint counter, before sending another message.
ATTENTION: this works only if they have the same amount of points !!!!"""
synchronizing_list = []
synchronizing_lock = Lock()
#===============================================================================
# UR Socket
#===============================================================================
class URSocket(ActuatorSocket):
    
    MULT = 100000.0 # for converting the floats to integers
    
    
    def __init__(self, sock, parent, identifier, **params):
        
        ActuatorSocket.__init__(self, sock, parent, identifier, **params)  
        self.stack_size = 5
        self.byteorder = "!"        
        self.msg_command_length = 48
        
        self.synchronize = False
        
        self.pose_cartesian_time_stamp = time.time()
        self.analog_in_time_stamp = 0.0
        self.ur_data_time_stamp = 0.0
        
        self.counter = 0
                
        UR_SERVER_PORT = 30002
        #UR1_IP = "10.0.0.11"
        #UR2_IP = "10.0.0.12"        
        #UR1_IP = "192.168.10.43"
        #UR2_IP = "192.168.10.25"
        
        if self.socket_type == "SND":
            
            "Calculate speed of UR!"
            synchronizing_lock.acquire()
            synchronizing_list.append(self.get_waypoint_counter())
            self.sync_index = len(synchronizing_list) - 1
            synchronizing_lock.release()
            
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ip = self.ip
            self.server_socket.connect((ip, UR_SERVER_PORT))
        
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
            """ ATTENTION! time stamp does not work here, but we know the URs cycle rate of 0.008 seconds.
            So we use our own counter for putting on the queue and increment it with 0.008. """
            msg_current_pose_cartesian = self.get_current_pose_cartesian(raw_msg)
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            
            """
            dQ_speed = globals.RECEIVE_QUEUES.get(self.identifier, MSG_CURRENT_SPEED)
            if dQ.length() > 1:
                # get the last one 
                last_pose, ts = dQ.get(keep_data = True, time_stamp = True)
                vx, vy, vz = msg_current_pose_cartesian[0] - last_pose[0], msg_current_pose_cartesian[1] - last_pose[1], msg_current_pose_cartesian[2] - last_pose[2]
                vlength = math.sqrt(vx*vx + vy*vy + vz*vz)
                try:
                    speed = vlength/math.fabs(self.pose_cartesian_time_stamp - ts)
                    #dQ_speed.put(speed, self.pose_cartesian_time_stamp, wait=True) 
                    dQ_speed.put(speed, wait=True) 
                except ZeroDivisionError:
                    pass
            """
            
            #if self.identifier == "UR1":
            #    print "UR1 Pose %i: " % self.counter, time_stamp, msg_current_pose_cartesian
            #    self.counter += 1
            
            dQ.put(msg_current_pose_cartesian, time_stamp, wait = True) 
            #dQ.put(msg_current_pose_cartesian, self.pose_cartesian_time_stamp, wait=True) 
            #self.pose_cartesian_time_stamp += 0.008
            
            
        
        elif msg_id == MSG_CURRENT_SPEED:
            msg_current_speed = self.get_speed(raw_msg)
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_current_speed, time_stamp, wait = True) 
            
            
        elif msg_id == MSG_CURRENT_POSE_JOINT:
            msg_current_pose_joint = self.get_current_pose_joint(raw_msg)
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_current_pose_joint, time_stamp, wait = True)   
                        
        elif msg_id == MSG_ANALOG_IN:
            """ ATTENTION! time stamp does not work here, but we know the URs cycle rate of 0.008 seconds.
            So we use our own counter for putting on the queue and increment it with 0.008. """
            msg_analog_in = self.get_analog_in(raw_msg)
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            #dQ.put(msg_analog_in, time_stamp, wait = True)
            dQ.put(msg_analog_in, self.analog_in_time_stamp, wait = True)
            self.analog_in_time_stamp += 0.008
        
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
            
        elif msg_id == MSG_UR_DATA:
            ur_data = self.get_ur_data(raw_msg)
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(ur_data, self.ur_data_time_stamp)
            self.ur_data_time_stamp += 0.008
            
        else:
            print "%sSocket: msg_id %d" % (self.identifier, msg_id)
            print "%sSocket: Message identifier unknown:  %s = %d, message: %s" % (self.identifier, msg_identifier_str_array[msg_id], msg_id, raw_msg)
            return   
    
    #===========================================================================
    def _send_command(self, cmd):
        """ MSG_COMMAND = 1 # [counter, position, orientation, optional values]
            called from handle stack: individual commands have to created for the specific actuator socket.
            UR: [x, y, z, ax, ay, az, acc, speed, radius, time]
        """
    
        "If self.synchronize == True, synchronize to the other client. = wait until they have the same waypoint counter"
        if self.synchronize == True:
            self.sync()
            #pass
    
        cmd = [c * self.MULT for c in cmd] 
        params = [self.msg_command_length, MSG_COMMAND, self.get_waypoint_counter()] + cmd
        #if self.identifier == "UR1": print "params", params, "\n len(params)", len(params)
        buf = struct.pack(self.byteorder + "%ii" % len(params), *params)
        self._send(buf)
        #print "\n%sSocket: Sent command %s with waypoint counter: %i.\n" % (self.identifier, str(cmd), self.get_waypoint_counter())          
    #===================================================================== 
    def send_speed(self, speed):
        # speed is between 0 and 1
        
        """
        msg_snd_len = 4 + 4
        params = [msg_snd_len, MSG_SPEED, speed * self.MULT]
        buf = struct.pack(self.byteorder + "3i", *params)
        self._send(buf)
        print "%sSocket: Sent speed: %f." % (self.identifier, speed)   
        """
        
        self.server_socket.send("set speed %f\n\n" % (speed))
        print "%sSocket: Sent speed: %f." % (self.identifier, speed)
    
    #===================================================================== 
    def send_stop(self):
        self.server_socket.send("stopl(0.1)\n\n")
        print "Sent STOP to %s." % (self.identifier)  
    #===================================================================== 
    def process_msg_cmd_executed(self, msg_counter):      
        #print "%sSocket:  %d len stack"  % (self.identifier, len(self.stack))
        if not len(self.stack) and self.get_stack_counter() == 0 and self.get_waypoint_counter() == msg_counter:
            print "%sSocket: self.publish_state(READY_TO_PROGRAM)"  % (self.identifier)
            self.publish_state(READY_TO_PROGRAM)
        else:
            self.publish_state(COMMAND_EXECUTED)
        
        self.publish_waypoint_counter_executed(msg_counter)
        #print "%sSocket: process_msg_cmd_executed, msg_counter %d." % (self.identifier, msg_counter) 
    #=====================================================================        
    def get_current_pose_cartesian(self, raw_msg):
        """ MSG_CURRENT_POSE_CARTESIAN = 5 # [position, orientation] """
        current_pose_cartesian_tuple = struct.unpack_from(self.byteorder + "%ii" % (6), raw_msg)
        current_pose_cartesian = [s / self.MULT for s in current_pose_cartesian_tuple]
        return current_pose_cartesian
    #===========================================================================
    """
    def update_current_speed(self, ur_data):
        dQ_speed = globals.RECEIVE_QUEUES.get(self.identifier, MSG_SPEED)
        dQ_ur_data = globals.RECEIVE_QUEUES.get(self.identifier, MSG_UR_DATA)
        last_data, ts = dQ_ur_data.get(time_stamp = True)
        if last_data:
            distance = (V3(last_data[:3]) - V3(ur_data[:3])).length()
            delta_t = self.ur_data_time_stamp - ts
            dQ_speed.put(distance/delta_t, self.ur_data_time_stamp)
    """
    #===========================================================================
    def get_analog_in(self, raw_msg):
        analog_in = struct.unpack_from(self.byteorder + "i", raw_msg)[0]/self.MULT
        return analog_in
    #===========================================================================
    def get_speed(self, raw_msg):
        speed = struct.unpack_from(self.byteorder + "i", raw_msg)[0]/self.MULT
        return speed
    #===========================================================================
    def get_current_pose_joint(self, raw_msg):
        """ MSG_CURRENT_POSE_JOINT = 5 # [j1, j2, j3, j4, j5, j6] """
        current_pose_joint_tuple = struct.unpack_from(self.byteorder + "%ii" % (6), raw_msg)
        current_pose_joint = [s / self.MULT for s in current_pose_joint_tuple]
        return current_pose_joint
    #===========================================================================
    def get_ur_data(self, raw_msg):
        #print "%sSocket: get_ur_data" % (self.identifier)
        ur_data_tuple = struct.unpack_from(self.byteorder + "%ii" % (7), raw_msg)
        ur_data = [s / self.MULT for s in ur_data_tuple]
        # self.update_current_speed(ur_data)
        return ur_data
    #===================================================================== 
    def sync(self):
        wpc = self.get_waypoint_counter()   
        
        synchronizing_lock.acquire()
        synchronizing_list[self.sync_index] = wpc
        synchronizing_lock.release()
        
        #print "SYNC: %sSocket: waiting to be synchronized to waypoint counter %s." % (self.identifier, wpc)
        #print "%s: synchronizing_list: %s, index: %d" % (self.identifier, synchronizing_list, self.sync_index)
        while len([a for a in synchronizing_list if a == synchronizing_list[0]]) != len(synchronizing_list):
            time.sleep(globals.SMALL_VALUE)
        #print "SYNC: %sSocket: synchronized with waypoint counter %s." % (self.identifier, wpc)
    #=====================================================================
    def handle_specific_case(self):
        return


#===============================================================================
class UR1Socket(URSocket):
    def __init__(self, socket, parent, identifier, **params):
        URSocket.__init__(self,  socket, parent, identifier, **params)
        #self.synchronize = True
        self.logging = False
#===============================================================================
class UR2Socket(URSocket):
    def __init__(self, socket, parent, identifier, **params):
        URSocket.__init__(self, socket, parent, identifier, **params)
        #self.synchronize = True
        self.logging = False
#=============================================================================== 

if __name__ == "__main__":
    
    
    UR_SERVER_PORT = 30002
    UR1_IP = "10.0.0.11"
    UR2_IP = "10.0.0.12"
    identifier = "UR1"
        
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = eval("%s_IP" % identifier)
    server_socket.connect((ip, UR_SERVER_PORT))
    print server_socket
    server_socket.close()
  
