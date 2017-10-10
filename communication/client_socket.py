'''
Created on 02.12.2013

@author: rustr
'''

from msg_identifiers import *

from threading import Thread
import struct
from Queue import Queue
import socket
import time
import sys

#===============================================================================
# Client Socket
#===============================================================================
class SimpleClientSocket(Thread):
    
    """ The Client Socket is the base for the specific client sockets 
    It can be used for both Receiver and Sender Sockets. """
    
    def __init__(self, socket, parent, identifier):
        
        Thread.__init__(self)
        self.daemon = True # true == die if main thread dies
    
        self.socket = socket
        self.identifier = identifier
        self.parent = parent
        
        self.msg_rcv = ""
        self.byteorder = "!" # "!" network, ">" big-endian, "<" for little-endian, see http://docs.python.org/2/library/struct.html
        self.byteorder = "<"
        
        self.running = True
        
        self.socket.settimeout(0.008)
        
        print ":::::::::created %s Socket." % identifier
        
        self.logging = False
        
        self.rcv_queue = Queue()
        self.snd_queue = Queue()
                                            
    #===========================================================================
    def read(self):
        
        """ The transmission protocol for messages is 
        [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier] """
        
        # 1. read msg length
        self.msg_rcv += self.socket.recv(4)
                
        if len(self.msg_rcv) < 4:
            return
        msg_length = struct.unpack_from(self.byteorder + "i", self.msg_rcv, 0)[0]
        
        #print "msg_length", msg_length
               
        # 2. read msg according to msg_length       
        self.msg_rcv += self.socket.recv(msg_length)
        if len(self.msg_rcv) < (msg_length + 4):
            return
        
        # 3. message identifier
        msg_id = struct.unpack_from(self.byteorder + "i", self.msg_rcv[4:8], 0)[0]
        
        #print "msg_id", msg_id
        
        # 4. rest of message, according to msg_length
        raw_msg = self.msg_rcv[8:(8 + msg_length - 4)]
        
        # 5. set self.msg_rcv to the rest
        self.msg_rcv = self.msg_rcv[(8 + msg_length - 4):]
        
        # 4. pass message id and raw message to process method
        self.process(msg_length, msg_id, raw_msg)
     
    def process(self, msg_len, msg_id, raw_msg):
        """
        The transmission protocol for messages is:
        [length msg in bytes] [msg identifier] [other bytes which will be read 
        out according to msg identifier]
            
            identifiers of receive messages:
            MSG_COMMAND_RECEIVED = 4 # [index]
            MSG_CURRENT_POSE_CARTESIAN = 5 # [position, orientation]
            MSG_CURRENT_POSE_JOINT = 6 # [j1, j2, j3, j4, j5, j6]
            MSG_STRING = 7 # [string] 
            MSG_FLOAT_ARRAY = 8 # [float, float, ...] """
        
        rcv_queue = self.rcv_queue
                                       
        if msg_id == MSG_FLOAT_LIST: 
            msg_float_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "f", raw_msg)
            msg_float_list = [item for item in msg_float_tuple]
            
            rcv_queue.put(msg_float_list)
            
            self.perform_operation() 
    
        else:
            print "%sSocket: msg_id %d" % (self.identifier, msg_id)
            print "%sSocket: Message identifier unknown:  %s = %d, message: %s" % (self.identifier, msg_identifier_str_array[msg_id], msg_id, raw_msg)
            return   
    

    def perform_operation(self):
        """
        This method is overwritten 
        """
        pass
         

    def send(self, msg_id, msg = None):
        """ 
        The transmission protocol for send messages is:
        [length msg in bytes] [msg identifier] [other bytes which will be read 
        out according to msg identifier]
        """
        buf = None
        
        if msg_id == MSG_QUIT:
            msg_snd_len = 4
            params = [msg_snd_len, msg_id]
            buf = struct.pack(self.byteorder + "2i", *params)
              
        elif msg_id == MSG_FLOAT_LIST:
            msg_snd_len = struct.calcsize(str(len(msg)) + "f") + 4
            msg = [float(item) for item in msg] # change tuple to list
            params = [msg_snd_len, msg_id] + msg           
            buf = struct.pack(self.byteorder + "2i" + str(len(msg)) +  "f", *params)
            print "%sSocket: Sent message %s." % (self.identifier, msg_identifier_str_array[msg_id])
    
        else:
            print "%sSocket: Message identifier unknown:  %s = %d, message: %s" % (self.identifier, msg_identifier_str_array[msg_id], msg_id, msg)
            return   
        
        self.socket.send(buf)
    
    #===========================================================================
    def run(self):
        snd_queue = self.snd_queue

        while self.running:
            
            # process send command
            if not snd_queue.empty():
                
                msg_id, msg = snd_queue.get()
                
                try:
                    self.send(msg_id, msg)
                except socket.timeout:
                    print "Timeout here... 1"
                    time.sleep(0.5)
                    self.send(msg_id, msg)
                    
                except socket.error as e:
                    if e.errno == 10054 or e.errno == 10053:
                        print "%s: Client has been disconnected." % (self.identifier)
                        self.parent.close()                        
                    else:
                        print "CLIENT SOCKET ERROR 1", e
                        raise e
            
            try:
                self.read() 
            except socket.timeout:
                pass # time outs are allowed
            except socket.error as e:
                if e.errno == socket.errno.WSAECONNRESET: # An existing connection was forcibly closed by the remote host
                    print "%sClient is not available anymore." % self.identifier
                    self.running = False
                else:
                    print "CLIENT SOCKET ERROR 2", e
                    print "e.errno", e.errno
                    raise e
            
        self.parent.input.remove(self.socket)
        self.socket.close()
        print "%sClient: closed." % self.identifier
                

#===============================================================================

if __name__ == "__main__":
    print  msg_identifier_str_array[10]