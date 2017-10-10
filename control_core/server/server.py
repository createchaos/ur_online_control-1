'''
S.A.N.S V0.1

Created on Nov 2, 2012
@author: Kathrin & Romana
'''
import sys
import select 
import socket 
from threading import Thread, Lock

from globals import * 
import struct

from actuator_sockets import *
from sensor_sockets import *
from cad_sockets import *
from socket_container import SocketContainer


#===============================================================================
class Server(Thread):
    
    def __init__(self):
        """ Server waits for incoming connections on port 30003, from an incoming 
        connection a base socket is created. The base socket expects and receives 
        the identifier message, according to that id the specific socket container 
        including the sender and the receiver is created.
        
        TODO:  Check if client has disconnected, emit signal and 
        remove it from self.client_identifiers and self.socket_containers!
        """
        Thread.__init__(self)
        
        self.daemon = True # die if main dies

        self.address = '' # leave it open for outer (192. ...) and inner (127. ...) connections
        self.port = 30003
        self.client_identifiers = [] # e.g. "Rhino", "ABB", ...
        self.socket_containers = [] # e.g. SocketContainer("Rhino"), SocketContainer("ABB"), ...
        
        self.input = []
        self.running = False
        
        self.lock = Lock()

    #===========================================================================
    def run(self):
        
        self.start_listening()
        
        while self.running: 
            
            self.lock.acquire()
            try:
                inputready, outputready, exceptready = select.select(self.input, [], []) 
            except socket.error as e: 
                
                if e.errno == socket.errno.EBADF: # raise error(EBADF, 'Bad file descriptor')
                    if len(self.socket_containers) == 0 and len(self.input) == 1:
                        break
                    else:
                        print e
                        raise
                else:
                    raise
            except:
                e = sys.exc_info()[0]
                print e
                raise
                
            "TODO: error: (10038, 'An operation was attempted on something that is not a socket')"
            
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
            self.lock.release()
                    
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
        self.read_identifier(sock, ip)
    #===========================================================================
    def read_identifier(self, sock, ip):
        byteorder = "!"
        
        "1. read msg length"
        msg_rcv = sock.recv(4)
    
        while len(msg_rcv) < 4:
            time.sleep(0.5) # wait a little and try to read again.
            print "SERVER: 1, Cannot read message length, trying to read again..."
            msg_rcv += sock.recv(4)
            
        """
        if len(msg_rcv) < 4:
            print "Client is not sending its identifier, closing socket."
            self.input.remove(sock)
            sock.close()
            return
        """
        
        
        msg_length = struct.unpack_from(byteorder + "i", msg_rcv, 0)[0]
        
        " TODO: better solution, here HACK for detecting big and little endian messages"
        if msg_length > 30:
            byteorder = "<"
            msg_length = struct.unpack_from(byteorder + "i", msg_rcv, 0)[0]
            
        "2. read msg according to msg_length"
        msg_rcv += sock.recv(msg_length)
        
        while len(msg_rcv) < (msg_length + 4):
            time.sleep(0.5) # wait a little and try to read again.
            print "SERVER: 2, Client is not yet sending its identifier, trying to read again..."
            msg_rcv += sock.recv(msg_length)
        
        """
        if len(msg_rcv) < (msg_length + 4):
            print "Client is not sending its identifier, closing socket."
            self.input.remove(sock)
            sock.close()
            return
        """
        
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
            
            "According to id and type, create individual socket"
            
            if identifier not in self.client_identifiers:        
                container = SocketContainer(identifier, self)
                self.client_identifiers.append(identifier)
                self.socket_containers.append(container)            
            else:
                container = self.get_socket_container(identifier)
                
            " create specific client socket "
            if len(socket_type) == 1:
                if socket_type[0] == "RCV":
                    sender = eval(identifier + 'Socket(sock, container, identifier, sender=True)')
                    container.set_sender(sender)
                else: # socket_type[0] == "SND"
                    receiver = eval(identifier + 'Socket(sock, container, identifier, receiver=True)')
                    container.set_receiver(receiver)
                    
            else: # ["SND", "RCV"] or ["RCV", "SND"]
                "If both sender and receiver share the same socket, they should use send and read methods with socket lock."
                sender = eval(identifier + "Socket(sock, container, identifier, sender=True, socket_lock = True, ip = '%s')" % ip)
                receiver = eval(identifier + "Socket(sock, container, identifier, receiver=True, socket_lock = True, ip = '%s')" % ip)
                container.set_sender(sender)
                container.set_receiver(receiver)
        
        else:
            print "SERVER: msg_id %d unknown, disconnecting client." % msg_id
            self.input.remove(sock)
            sock.close()
            return

    #===========================================================================
    def get_socket_container(self, identifier):
        for cs in self.socket_containers:
            if cs.identifier == identifier:
                return cs
    #===========================================================================
    def close(self):
        self.server.close()
        print "SERVER: closed."
    #===========================================================================
    def quit(self): 
        """ Send to all the clients the quit message, wait for them to disconnect and 
        shut down the server """
        
        " Before closing: send all clients a quit message. "
        for id in self.client_identifiers:
            dQ = globals.SEND_QUEUES.get(id)
            dQ.put((MSG_QUIT, None))
        
        "TODO: wait if all clients are closed: see TODO 1."
        while len(self.client_identifiers) and len(self.input) > 1:
            time.sleep(1.0)
            print "SERVER: Waiting until all clients are disconnected..."
        self.running = False
        print "SERVER: quit done"
    #=====================================================================  
    def remove_client(self, container):
        self.lock.acquire()
        self.input.remove(container.sender.socket)
        if container.receiver.socket in self.input: self.input.remove(container.receiver.socket)
        self.lock.release()
        #container.sender.close()
        #container.receiver.close()
        self.socket_containers.remove(container)
        self.client_identifiers.remove(container.identifier)
    #=====================================================================    

def client(ip, port, message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, port))
    try:
        sock.sendall(message)
        response = sock.recv(1024)
        print "Received: {}".format(response)
    finally:
        sock.close()

if __name__ == "__main__":
    
    s = Server()
    s.start()
    
    ip = "127.0.0.1"
    port = 30003

    client(ip, port, "Hello World 1")
    client(ip, port, "Hello World 2")
    client(ip, port, "Hello World 3")
