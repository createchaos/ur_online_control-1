'''
// ============================ //
//        SANS V0.3             //
//    Created on 25.09.2014    //
//  @authors: Kathrin & Romana  //
// ============================ //
'''

from threading import Thread
from Queue import Queue

import socket
import struct
import time

import sys
import os
from Rhino.RhinoApp import WriteLine

"""
path = os.path.expanduser("~")
dirs = ["Dropbox", "SANS V0.6 Lite SWC", "02_Fabrication_Software", "SANS SWC"]
for d in dirs: path = os.path.join(path, d)
print path
sys.path.append(path)
"""

from globals.message_identifiers import *


class Client(): 

    """ A simple client that is looping to receive some data, but it can also send data. """
    
    def __init__(self, identifier, host, port):
        
        self.identifier = identifier
        self.host = host
        self.port = port        
        self.socket_type = "SND RCV"
        self.byteorder = "!" # "!" network, ">" big-endian, "<" for little-endian, see http://docs.python.org/2/library/struct.html
        self.byteorder = "<"
        " For receiving messages "
        self.msg_rcv = ""
        self.msg_len_rcv = "" # test for checking to read in properly
        self.sndQ = Queue()
        self.rcvQ = Queue()
        self.timeout = 1.0
        self.running = False

                   
    #===========================================================================
    def _run_as_sender(self):
        
        while self.running:            
            try:
                while not self.sndQ.empty():
                    msg_id, msg = self.sndQ.get(block=True, timeout=None)
                    self._send(msg_id, msg)
                
            except socket.timeout, e:                
                WriteLine("%s: socket.timeout in sender:" % (self.identifier) , e)
                self.close()
            except socket.error, e:
                WriteLine("%s: socket.error in sender:" % (self.identifier) , e)
                self.running = False
        
    #===========================================================================
    def _run_as_receiver(self):
        
        while self.running:        
            try:
                self.read()
                
            except socket.timeout, e:
                err = e.args[0]
                if err == 'timed out':
                    continue # recv timed out, retry ...
                else:
                    pass
                
            except socket.error, e:
                WriteLine("%s: socket.error in receiver:" % (self.identifier) , e)
                self.running = False
        self.close()
                     
    #===========================================================================
    def start(self):
        self.sender_thread.start()
        self.receiver_thread.start()
    #===========================================================================
    def connect_to_server(self):
        self.running = False
        
        try:
            self.socket = socket.create_connection((self.host, self.port), timeout=self.timeout) 
                        
            self.running = True
            self.sender_thread = Thread(target = self._run_as_sender)
            self.sender_thread.daemon = False
            
            self.receiver_thread = Thread(target = self._run_as_receiver)
            self.receiver_thread.daemon = False
            
            self.start()
            
            self.send_id()
            
            WriteLine("%s: Successfully connected to server %s on port %d." % (self.identifier, self.host, self.port))
            return True
        except:
            WriteLine("%s: Server %s is not available on port %d." % (self.identifier, self.host, self.port))
            self.running = False
            return False
    
    #===========================================================================
    def send_id(self):
        
        msg = "%s %s" % (self.identifier, self.socket_type)
        self.send(MSG_IDENTIFIER , msg) 
        
    #===========================================================================
    def close(self):
        
        self.running = False
        self.socket.close()
                
        time.sleep(0.1)
                
        try:
            self.sender_thread.join()
            self.receiver_thread.join()
            WriteLine("%s: Successfully joined threads." % self.identifier)
        
        except RuntimeError:
            pass
            #WriteLine("%s: Cannot join thread." % self.identifier)
        
    #===========================================================================
    def send(self, msg_id, msg = None):
        self.sndQ.put([msg_id, msg], block=True, timeout=None)
    #===========================================================================
    def _send(self, msg_id, msg = None):
        """ send message according to message id """
        
        buf = None
        
        if msg_id == MSG_FLOAT_LIST:
            msg_snd_len = struct.calcsize(str(len(msg)) + "f") + 4 # float array: length of message in bytes: len*4
            params = [msg_snd_len, msg_id] + msg
            buf = struct.pack(self.byteorder + "2i" + str(len(msg)) +  "f", *params)
        
        elif msg_id == MSG_IDENTIFIER:
            msg_snd_len = len(msg) + 4
            params = [msg_snd_len, msg_id, msg]
            buf = struct.pack(self.byteorder + "2i" + str(len(msg)) +  "s", *params)
        
        else:
            WriteLine("%s: Message identifier unknown:  %s = %d, message: %s" % (self.identifier, msg_identifier_str_array[msg_id], msg_id, msg))
            return   
           
        self.socket.send(buf)
        WriteLine("%s: Sent message: %s to server " % (self.identifier, msg_identifier_str_array[msg_id]))
          
 
    #===========================================================================
    def read(self):
        """ The transmission protocol for messages is 
        [length msg in bytes] [msg identifier] [other bytes which will be read out according to msg identifier] """
        
        "1. read msg length"
        self.msg_rcv += self.socket.recv(4)
        if len(self.msg_rcv) < 4:
            return
        msg_length = struct.unpack_from(self.byteorder + "i", self.msg_rcv, 0)[0]   
        
        "2. read msg according to msg_length"
        self.msg_rcv += self.socket.recv(msg_length)
        
        "3. message identifier"
        self.msg_rcv = self.msg_rcv[4:]
        msg_id = struct.unpack_from(self.byteorder + "i", self.msg_rcv[:4], 0)[0]
        
        raw_msg = self.msg_rcv[4:]
        
        " reset msg_rcv"
        self.msg_rcv = ""
        
        "4. pass message id and raw message to process method "
        self.process(msg_length, msg_id, raw_msg)
    
    #===========================================================================
    def process(self, msg_len, msg_id, raw_msg):
        
        msg = None
        
        if msg_id == MSG_QUIT:
            WriteLine("%s: Received MSG_QUIT" % self.identifier)
            self.close()
        if msg_id == MSG_FLOAT_LIST:
            WriteLine("%s: Received MSG_FLOAT_LIST" % self.identifier)
            msg_float_tuple = struct.unpack_from(self.byteorder + str((msg_len-4)/4) + "f", raw_msg)
            msg_float_list = [item for item in msg_float_tuple]
            self.rcvQ.put(msg_float_list)
        else:
            WriteLine("%s: Message identifier unknown: %d, message: %s" % (self.identifier, msg_id, raw_msg))
            return
        
        return(msg_id, msg)

if __name__ == "__main__":
    

    gh = Client("GH", "127.0.0.1", 30003)
    gh.connect_to_server()
    gh.send(MSG_FLOAT_LIST, [4.,5.])


    
        



     

