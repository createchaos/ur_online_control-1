'''
Created on 20.11.2013

@author: kathrind
'''

from client_socket import ClientSocket
import struct
from globals import *

#===============================================================================
# RhinoSocket
#===============================================================================
class GHSocket(ClientSocket):
    """ 
    The RhinoSocket can be in 2 different states: READY and BUSY
    """  
    
    def __init__(self, socket, parent, identifier, **params):
        ClientSocket.__init__(self, socket, parent, identifier, **params)
        #self.byteorder = "!" # "!" network, ">" big-endian, "<" for little-endian, see http://docs.python.org/2/library/struct.html
        self.byteorder = "<"
        self.msg_command_length = 28    
    #=====================================================================        
    def send_command(self, cmd):
        """ MSG_COMMAND = 1 # [counter, position, orientation]
            called from send from CLientSocket: position and orientation in Euler Angles
            Rhino cmd: [x, y, z, a, b, c]
            FOR FUTURE DEVELOPMENT: Rhino simulator 
        """
        params = [self.msg_command_length, MSG_COMMAND] + cmd
        buf = struct.pack(self.byteorder + "2i6f", *params)
        self._send(buf)
        
        print "%sSocket: Sent pose to client %s." % (self.identifier, self.identifier)

    #=====================================================================        
    def get_current_pose_cartesian(self, raw_msg):
        """ MSG_CURRENT_POSE_CARTESIAN = 5 # [x, y, z, a, b, c]  
            FOR FUTURE DEVELOPMENT: Rhino simulator 
        """
        current_pose_cartesian_tuple = struct.unpack_from(self.byteorder + "6f", raw_msg)
        return current_pose_cartesian_tuple        
    #=====================================================================        
    def get_current_pose_joint(self, raw_msg):
        """ MSG_CURRENT_POSE_JOINT = 5 # [j1, j2, j3, j4, j5, j6] 
            FOR FUTURE DEVELOPMENT: Rhino simulator 
        """
        current_pose_joint_tuple = struct.unpack_from(self.byteorder + "6f", raw_msg)
        return current_pose_joint_tuple
    #=====================================================================
    def process_msg_cmd_executed(self, msg_counter=None):
        self.publish_state(READY)
    #=====================================================================
    
    
    

#===============================================================================
# RhinoSocket
#===============================================================================
class RhinoSocket(ClientSocket):
    """ 
    The RhinoSocket can be in 2 different states: READY and BUSY
    """  
    
    def __init__(self, socket, parent, identifier, **params):
        ClientSocket.__init__(self, socket, parent, identifier, **params)
        self.byteorder = "!"
        self.msg_command_length = 28    
    #=====================================================================        
    def send_command(self, cmd):
        """ MSG_COMMAND = 1 # [counter, position, orientation]
            called from send from CLientSocket: position and orientation in Euler Angles
            Rhino cmd: [x, y, z, a, b, c]
            FOR FUTURE DEVELOPMENT: Rhino simulator 
        """
        params = [self.msg_command_length, MSG_COMMAND] + cmd
        buf = struct.pack(self.byteorder + "2i6f", *params)
        self._send(buf)
        
        print "%sSocket: Sent pose to client %s." % (self.identifier, self.identifier)

    #=====================================================================        
    def get_current_pose_cartesian(self, raw_msg):
        """ MSG_CURRENT_POSE_CARTESIAN = 5 # [x, y, z, a, b, c]  
            FOR FUTURE DEVELOPMENT: Rhino simulator 
        """
        current_pose_cartesian_tuple = struct.unpack_from(self.byteorder + "6f", raw_msg)
        return current_pose_cartesian_tuple        
    #=====================================================================        
    def get_current_pose_joint(self, raw_msg):
        """ MSG_CURRENT_POSE_JOINT = 5 # [j1, j2, j3, j4, j5, j6] 
            FOR FUTURE DEVELOPMENT: Rhino simulator 
        """
        current_pose_joint_tuple = struct.unpack_from(self.byteorder + "6f", raw_msg)
        return current_pose_joint_tuple
    #=====================================================================
    def process_msg_cmd_executed(self, msg_counter=None):
        self.publish_state(READY)
    #=====================================================================

        
        
        