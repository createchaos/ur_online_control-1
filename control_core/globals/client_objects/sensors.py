'''
Created on 21.11.2013

@author: kathrind
'''


import Global
from Base import Base
import time

#===============================================================================
class Arduino(Base):
    def __init__(self, identifier):
        Base.__init__(self, identifier)
        
#===============================================================================
class SickTim5xx(Base):
    
    def __init__(self, identifier):
        Base.__init__(self, identifier)
        self.emit_set_busy_state()
        
    def wait(self, state):
        while self.state != state:
            time.sleep(0.001)
            
    def set_mode(self, mode="request", amount = 1, range_min=45, range_max=135):
        """ mode can be as request single scans with range and number, or streaming mode """
        # mode = "request"
        # mode = "stream"

        if mode == "request":
            self.send(Global.MSG_OPERATION, "RequestScan")
        if mode == "continuous":
            self.send(Global.MSG_OPERATION, "StreamScan")
            self.send(Global.MSG_COMMAND, [amount, range_min, range_max])
        
    def query_scan(self, amount = 50, range_min=-45, range_max=225):
        "the scanner returns a float array with x and y values"
        
        self.send(Global.MSG_COMMAND, [amount, range_min, range_max])
        # self.wait(Global.ClientStates.READY)
        
        dQ_float_tuple = Global.RECEIVE_QUEUES.get(self.identifier, Global.MSG_FLOAT_LIST)
        float_tuple = dQ_float_tuple.get(wait=True)
        
        print float_tuple
        
        if float_tuple:        
            return [item for item in float_tuple]
        else:
            return []
        
    def get_scan_from_queue(self):
        
        dQ_float_tuple = Global.RECEIVE_QUEUES.get(self.identifier, Global.MSG_CURRENT_SCAN)
        float_tuple = dQ_float_tuple.get(wait=True)
        
        if float_tuple:        
            return [item for item in float_tuple]
        else:
            return [] 
        
#===============================================================================