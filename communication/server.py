'''
Created on 23.08.2016

@author: rustr
'''

import sys
import select 
import socket 
from threading import Thread
import time

from client_socket import *
from msg_identifiers import *
import struct

#===============================================================================
class SimpleServer(Thread):
    
    def __init__(self):
        
        Thread.__init__(self)
        
        self.daemon = False # True = die if main dies

        self.address = '127.0.0.1'
        self.port = 30003
        self.client_identifiers = []
        self.client_sockets = [] 
        
        self.input = []
        self.running = False
        
        self.client_socket_type = ""
        
    
    #===========================================================================
    def create_client_socket(self, sock, identifier):
        
        client_socket = SimpleClientSocket(sock, self, identifier)
        return client_socket
        
    #===========================================================================
    def run(self):
        
        self.start_listening()

        while self.running: 
            
            try:
                inputready, outputready, exceptready = select.select(self.input, [], []) 
            
            
            except socket.error as e: 
                
                if e.errno == socket.errno.EBADF: # raise error(EBADF, 'Bad file descriptor')
                    print len(self.input)
                    #pass
                else:
                    raise
                
            except select.error:
                print "An operation was attempted on something that is not a socket"
            
            except:
                e = sys.exc_info()[0]
                print "SERVER ERROR 2:", e
                raise
                            
            for s in inputready: 

                if s == self.server: 
                    try:
                        sock, address = self.server.accept()
                        self.incoming_connection(sock, address)
                    except socket.error as e: 
                        if e.errno == socket.errno.EBADF: # raise error(EBADF, 'Bad file descriptor')
                            break
                        else:
                            raise
                    
        self.close()
    #===========================================================================
    def start_listening(self):
        try:
            backlog = 5
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((self.address, self.port)) 
            self.server.listen(backlog)
            self.input = [self.server]
            print "SERVER: running on port %d." % self.port
            self.running = True
        except:
            self.close()
    #===========================================================================
    def incoming_connection(self, sock, address):
        """ from any incoming connection a BaseSocket is created.
        According to the identifier it will be accepted or refused. If accepted, the specific ClientSocket is created. """
        ip, port = address
        print "SERVER: ____________________________________incoming connection from %s, at port %d. " % (ip, port) 
        self.input.append(sock)
        self.read_identifier(sock)
    #===========================================================================
    def read_identifier(self, sock):
        byteorder = "!"
        
        "1. read msg length"
        msg_rcv = sock.recv(4)
    
        while len(msg_rcv) < 4:
            time.sleep(0.5) # wait a little and try to read again.
            print "SERVER: 1, Cannot read message length, trying to read again..."
            msg_rcv += sock.recv(4)
                    
        msg_length = struct.unpack_from(byteorder + "i", msg_rcv, 0)[0]
        
        # TODO: better solution, here HACK for detecting big and little endian messages
        if msg_length > 30:
            byteorder = "<"
            msg_length = struct.unpack_from(byteorder + "i", msg_rcv, 0)[0]
            
        "2. read msg according to msg_length"
        msg_rcv += sock.recv(msg_length)
        
        
        while len(msg_rcv) < (msg_length + 4):
            time.sleep(0.5) # wait a little and try to read again.
            print "SERVER: 2, Client is not yet sending its identifier, trying to read again..."
            msg_rcv += sock.recv(msg_length)
                
        "3. message identifier"
        msg_rcv = msg_rcv[4:]
        msg_id = struct.unpack_from(byteorder + "i", msg_rcv[:4], 0)[0]
        raw_msg = msg_rcv[4:]
        
        if msg_id == MSG_IDENTIFIER:
        
            " Identifier RCV or Identifier SND or Identifier RCV SND "
            
            message_ids = str(raw_msg).split(" ")
            identifier = message_ids[0] 
            socket_type = [message_ids[1]]
            if len(message_ids) == 3: socket_type = [message_ids[1], message_ids[2]] # if we have both sender and receiver in one socket
            
            
            self.client_socket = self.create_client_socket(sock, identifier)
            self.client_socket.start()
            self.client_identifiers.append(identifier)
            self.client_sockets.append(self.client_socket)   
            

        else:
            print "SERVER: msg_id %d unknown, disconnecting client." % msg_id
            self.input.remove(sock)
            sock.close()
            return

    #===========================================================================
    def close(self): 
        """ Send to all the clients the quit message, wait for them to disconnect and 
        shut down the server """
        
        for cs in self.client_sockets:
            cs.running = False
            self.input.remove(cs.socket)
            cs.socket.close()
            cs.join()
    
        self.running = False
        print "SERVER: quit done"


#===============================================================================

"""
def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()
"""

if __name__ == "__main__":
    
    server = SimpleServer()
    server.run() # dont use as thread
    #server.start() 
    
    #ip = "127.0.0.1"
    #port = 30003

    #client(ip, port, "Hello World 1")
    #client(ip, port, "Hello World 2")
    #client(ip, port, "Hello World 3")
