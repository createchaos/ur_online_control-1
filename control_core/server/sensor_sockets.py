'''
Created on 20.11.2013

@author: kathrind
'''

from client_socket import ClientSocket
import struct
import globals


#===============================================================================
class SensorSocket(ClientSocket):
    """ 
    The sensor can be in 2 different states: READY=1 and BUSY=2.
    """
    
    def __init__(self, socket, parent, identifier, **params):
        ClientSocket.__init__(self, socket, parent, identifier, **params)
        
        self.byteorder = "!" # "!" network, ">" big-endian, "<" for little-endian, see http://docs.python.org/2/library/struct.html
        self.msg_command_length = 16
            
    #===========================================================================
    def process(self, msg_len, msg_id, raw_msg):
        """ The transmission protocol for messages is 
        [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier]"""

        if msg_id == globals.MSG_COMMAND_EXECUTED:
            "Actuators send the waypoint counter together with the msg_id, other Clients just the msg_id."
            if len(raw_msg):
                msg_counter = struct.unpack_from(self.byteorder + "i", raw_msg)[0]
            else:
                msg_counter = None
            self.process_msg_cmd_executed(msg_counter)
        
        elif msg_id == globals.MSG_STRING:
            msg_string = struct.unpack_from(self.byteorder + str(msg_len-4) + "s", raw_msg)[0]
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_string, wait = True)    
                    
        elif msg_id == globals.MSG_FLOAT_LIST: 
            msg_float_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "f", raw_msg)
            msg_float_list = [item for item in msg_float_tuple]
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_float_list, wait = True)
            
            "Replaces the message MSG_COMMAND_EXECUTED"
            #self.process_msg_cmd_executed()
            
        elif msg_id == globals.MSG_CURRENT_SCAN: 
            msg_float_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "f", raw_msg)
            msg_float_list = [item for item in msg_float_tuple]
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_float_list, wait = True)

        else:
            print "%sSocket: msg_id %d" % (self.identifier, msg_id)
            print "%sSocket: Message identifier unknown:  %s = %d, message: %s" % (self.identifier, globals.msg_identifier_str_array[msg_id], msg_id, raw_msg)
            return
          
    #=====================================================================
    def process_msg_cmd_executed(self, msg_counter=None):
        self.publish_state(globals.READY)
    #=====================================================================


#===============================================================================
# SICKTIMXX
#===============================================================================
class SickTim5xxSocket(SensorSocket):
        
    def __init__(self, socket, parent, identifier, **params):
        SensorSocket.__init__(self, socket, parent, identifier, **params)
        self.byteorder = "!"
        self.msg_command_length = 16
    #===========================================================================
    def send_command(self, cmd):
        """ MSG_COMMAND = 1 # [-range = -45, + range = 225, amount]
            range in degrees and amount of scans
        """
        params = [self.msg_command_length, globals.MSG_COMMAND] + cmd
        buf = struct.pack(self.byteorder + "2i3f", *params)
        self._send(buf)
        print "%sSocket: Send command to client %s. " % (self.identifier, self.identifier)
#===============================================================================

class ArduinoSocket(SensorSocket):
    def __init__(self, socket, parent, identifier, **params):
        SensorSocket.__init__(self, socket, parent, identifier, **params)
        self.byteorder = "<" # "!" network, ">" big-endian, "<" for little-endian, see http://docs.python.org/2/library/struct.html
    #===========================================================================
    def process(self, msg_len, msg_id, raw_msg):
        """ The transmission protocol for messages is 
        [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier]"""

        if msg_id == globals.MSG_COMMAND_EXECUTED:
            if len(raw_msg):
                msg_counter = struct.unpack_from(self.byteorder + "i", raw_msg)[0]
            else:
                msg_counter = None
            self.process_msg_cmd_executed(msg_counter)
        
        elif msg_id == globals.MSG_STRING:
            msg_string = struct.unpack_from(self.byteorder + str(msg_len-4) + "s", raw_msg)[0]
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_string, wait = True)    
                    
        elif msg_id == globals.MSG_FLOAT_LIST: 
            msg_float_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "f", raw_msg)
            msg_float_list = [item for item in msg_float_tuple]
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_float_list, wait = True)
        
        elif msg_id == globals.MSG_INT_LIST: 
            msg_int_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "i", raw_msg)
            " /100.0 = ATTENTION HACK!! TODO: how to send floats from Arduino! "
            msg_float_list = [item/1000.0 for item in msg_int_tuple] 
            dQ = globals.RECEIVE_QUEUES.get(self.identifier, msg_id)
            dQ.put(msg_float_list, wait = True)
            
        else:
            print "%sSocket: msg_id %d" % (self.identifier, msg_id)
            print "%sSocket: Message identifier unknown:  %s = %d, message: %s" % (self.identifier, globals.msg_identifier_str_array[msg_id], msg_id, raw_msg)
            return
          
    #=====================================================================
#===============================================================================
    

