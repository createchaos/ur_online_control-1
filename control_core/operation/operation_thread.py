'''
S.A.N.S V0.1

Created on Nov 5, 2012
@author: Kathrin & Romana
'''

"""
The OperationThread waits for all necessary clients, according to the globally selected Operation, to connect and
for the operation_run signal from the GUI to enter an event driven loop.
The Operation calculates stuff, puts calculated stuff on client queues, waits for messages from various clients to
process it further. This operation_class is looped until the operation_run signal is set to False or loop.terminate() was called.
"""

import globals
import time

from globals.client_objects import *
from threading import Thread
import sys
import operations

#===============================================================================
class OperationThread(Thread):
    
    def __init__(self, selected_operation):
        Thread.__init__(self)
                
        self.connected_clients = []
        "A counter for counting the thread loops"
        self.counter = 0
        self.running = True
        
        self.selected_operation = selected_operation
        self.operation_run = False
        
        self.storage = None # used by the Operation to store data
        self.wait_for_key_input = False
        

    #===========================================================================               
    def terminate(self):
        self.running = False
    #===========================================================================
    def check_if_all_connected(self):
        connected_clients = globals.CLIENT_OBJECTS.get_all_connected_client_identifiers()
        "Check if we have new clients"
        if len(self.connected_clients) < len(connected_clients):
            cccp = self.selected_operation.clients[:]
            for c in connected_clients:
                if c in cccp: cccp.remove(c)
            print "OPERATION_THREAD: connected clients: %s" % connected_clients
            if len(cccp):
                print "OPERATION_THREAD: clients still necessary to start operation: %s" % cccp
            self.connected_clients = connected_clients
                 
        if not len(connected_clients): return False
        for c in self.selected_operation.clients:
            if not c in connected_clients:
                return False
        return True   
    #===========================================================================
    def run(self):
        
        while self.running:
            print "OPERATION_THREAD: selected operation: %s" % self.selected_operation.name
            "First check if all clients are connected:"
            all_connected = self.check_if_all_connected()
            while not all_connected:
                all_connected = self.check_if_all_connected()
                time.sleep(globals.SMALL_VALUE)
                
            print "OPERATION_THREAD: Now all clients are connected."
            # then wait for key input
            if self.wait_for_key_input: # or self.counter >= 1: 
                print "OPERATION_THREAD: Enter any key to continue"
                sys.stdin.read(1)
            
            "Execute the selected operation"
            getattr(operations, self.selected_operation.name)(self)
            "The conditions before entering the loop again"
            self.counter += 1
            print "OPERATION_THREAD: --------------------- loop counter: %d" % self.counter
        #=======================================================================
        " If self.terminate() was called it will stop here "
        self.reset()
        
    #===========================================================================
    def restart(self):
        self.running = True
        self.start()
    #===========================================================================   
    def reset(self):
        self.counter = 0
        self.operation_run = False
        #self.quit()
        print "OPERATION_THREAD: has been terminated."
        
    #===========================================================================


if __name__ == "__main__":
    getattr(operations, "NewTest")(None)