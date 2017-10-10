'''
Created on 14.11.2013

@author: rustr
'''
from threading import Lock
from globals.client_objects import UR, UR1, UR2, GH, Rhino

#===============================================================================
class ClientObjectsContainer():
    """ A container for all Client Objects for various clients 
    Client Objects can be Actuators (UR, ABB, etc.) or Sensors """
    " Works like the DataQueues Class"
    
    def __init__(self):
        self.objects = []
        self.lock = Lock()
    
    def get_all_connected_client_identifiers(self):
        self.lock.acquire()
        ids = [o.identifier for o in self.objects]
        self.lock.release()
        return ids
    
    def append(self, identifier):
        self.lock.acquire()
        obj = eval("%s('%s')" % (identifier, identifier))
        self.objects.append(obj)
        self.lock.release()
    
    def get(self, identifier):
        self.lock.acquire() # cannot be modified while iterating
        obj = None
        for o in self.objects:
            if o.identifier == identifier:
                obj = o
                break
        self.lock.release()
        return obj
#===============================================================================