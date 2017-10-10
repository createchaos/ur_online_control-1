'''
Created on 20.11.2013

@author: rustr
'''
import globals

from base import Base

#===============================================================================
class GH(Base):
    
    def __init__(self, identifier):
        Base.__init__(self, identifier)
        
    def send(self, msg_id, msg):
        self.set_busy_state()
        self.sndQ.put((msg_id, msg))
        
    def send_float_list(self, msg):
        self.set_busy_state()
        self.sndQ.put((globals.MSG_FLOAT_LIST, msg))
        
    def get_command(self):
        """ UR  >   [x, y, z, ax, ay, az] (Axis-angle) """
    
        dQ_float_tuple = globals.RECEIVE_QUEUES.get(self.identifier, globals.MSG_COMMAND)
        cmd = dQ_float_tuple.get(wait=True)

        return cmd
    
    def get_commands(self, number):
        """ UR  >   [x, y, z, ax, ay, az] (Axis-angle) """
        
        print "get cmd"
        cmds = []
        for n in range(number):
            dQ_float_tuple = globals.RECEIVE_QUEUES.get(self.identifier, globals.MSG_COMMAND)
            cmd = dQ_float_tuple.get(wait=True)
            cmds.append(cmd)

        return cmds
        
#===============================================================================

#===============================================================================
class Rhino(Base):
    
    def __init__(self, identifier):
        Base.__init__(self, identifier)
        
        " before operation is not set > rhino state is busy "
        self.set_busy_state()
        
    def send(self, msg_id, msg):
        self.set_busy_state()
        self.sndQ.put((msg_id, msg))
        
    def send_float_list(self, msg):
        self.set_busy_state()
        self.sndQ.put((globals.MSG_FLOAT_LIST, msg))
        
    def get_command(self):
        """ UR  >   [x, y, z, ax, ay, az] (Axis-angle) """
        
        print "get cmd"
        dQ_float_tuple = globals.RECEIVE_QUEUES.get(self.identifier, globals.MSG_COMMAND)
        cmd = dQ_float_tuple.get(wait=True)

        return cmd
    
    def get_commands(self, number):
        """ UR  >   [x, y, z, ax, ay, az] (Axis-angle) """
        
        print "get cmd"
        cmds = []
        for n in range(number):
            dQ_float_tuple = globals.RECEIVE_QUEUES.get(self.identifier, globals.MSG_COMMAND)
            cmd = dQ_float_tuple.get(wait=True)
            cmds.append(cmd)

        return cmds
        
#===============================================================================
    
if __name__ == "__main__":
    
    gh = GH("GH")
    print gh.state
    print gh.get_command()