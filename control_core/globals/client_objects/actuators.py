'''
Created on 29.10.2013

@author: rustr
'''

import globals
from base import Base
import time
from globals.useful_functions import clamp
from globals.message_identifiers import *

#===============================================================================
def send_stop_to_ur_robot(identifier):
    import socket
    UR_SERVER_PORT = 30002
    obj = globals.CLIENT_OBJECTS.get(identifier)
    ip = obj.sender_ip
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, UR_SERVER_PORT))
    s.send("stopl(0.1)\n\n")
    s.close()
    print "Sent STOP to %s on ip %s." % (identifier, ip)

#===============================================================================
# ActuatorBase
#===============================================================================
class ActuatorBase(Base):
    """ This is the base class for all Actuators """
    def __init__(self, identifier):
        Base.__init__(self, identifier)
        self.waypoint_counter = 0 # the current waypoint
    
    def get_waypoint_counter(self):
        return self.waypoint_counter
        
    def ready(self):
        return self.ready_to_program()
    
    def ready_to_program(self):
        return self.state == globals.READY_TO_PROGRAM
    
    def command_executed(self):
        return self.state == globals.COMMAND_EXECUTED
        
    def set_ready_state(self):
        self.set_state(globals.READY_TO_PROGRAM)
    
    def set_busy_state(self):
        self.set_state(globals.EXECUTING)
        
    def send_command(self, parent, **params):
        "Will be overwritten be the derivations"
        pass
    
    def set_tool(self, current_pose):
        pass
    
    def set_waypoint_counter_executed(self, msg_counter):
        self.lock.acquire()
        self.waypoint_counter = msg_counter
        self.lock.release()
    
    def wait_for_waypoint_change(self):
        wpc = self.get_waypoint_counter()
        while wpc == self.get_waypoint_counter():
            time.sleep(globals.SMALL_VALUE)
        return self.get_waypoint_counter()
        
    
#===============================================================================
# UR
#===============================================================================
class UR(ActuatorBase):
    
    def __init__(self, identifier):
        ActuatorBase.__init__(self, identifier)
        
        self.acceleration = 1.2 # tool acceleration [m/s2], = 1.2 = default_value
        self.speed = 0.3 # tool speed [m/s] = 0.3 = default_value
        self.radius = 0.0 # blend radius (of target pose) [m]
        self.time = 0 # time [S]
    
    def send_movel(self, cmd):
        x, y, z, ax, ay, az, v, r = cmd
        msg = [x, y, z, ax, ay, az, 0, v, r, 0]
        print "CLIENT_OBJECTS: %s: %s" % (self.identifier, msg)
        
        self.set_busy_state()
        self.sndQ.put((globals.MSG_COMMAND, msg))        
    
    def get_speed(self, **params):
        return self.get_data_from_queue(globals.MSG_SPEED, **params)
    
    def get_angles(self, **params):
        return self.get_data_from_queue(globals.MSG_ANGLES, **params)
    
    def get_force(self, **params):
        return self.get_data_from_queue(globals.MSG_FORCE, **params)
    
    def send_speed(self, speed, max_speed):
        speed = speed/float(max_speed)
        speed = clamp(speed, 0.0, 1.0) # clamp speed between 0 and 1
        self.interruptQ.put((globals.MSG_SPEED, speed))    
    
    def get_pose_queue(self):
        return globals.RECEIVE_QUEUES.get(self.identifier, MSG_CURRENT_POSE_CARTESIAN)
    def get_speed_queue(self):
        return globals.RECEIVE_QUEUES.get(self.identifier, MSG_CURRENT_SPEED)
    
    def clear_data_queues(self):
        speed_queue = self.get_speed_queue()
        pose_queue = self.get_pose_queue()
        speed_queue.clear()
        pose_queue.clear()
    
    def stop(self):
        ActuatorBase.stop(self)
        send_stop_to_ur_robot(self.identifier)

#===============================================================================
class UR1(UR):
    def __init__(self, identifier):
        UR.__init__(self, identifier)
        
#===============================================================================
class UR2(UR):
        
    def __init__(self, identifier):
        UR.__init__(self, identifier)
#===============================================================================
        
if __name__ == "__main__":
    
    import numpy as np
    
    
    origin = V3(316.971187, -733.501764, 131.433461)
    x_axis = V3(0.016919, 0.999849, 0.003862)
    y_axis = V3(-0.999848, 0.016935, -0.004051)
    z_axis = V3(-0.004115, -0.003793, 0.999984)
    basisUR1 = Frame(origin, Rotation(x_axis,y_axis,z_axis))
    
    #733.502,316.971,-131.433
    
    t1 = Transformation(Frame.world(), basisUR1)
    
    print t1.transform(V3(0,0,0))
    print t1.transform(V3(287.668457, -68.693909, 450))
    
    ur1 = UR1("UR1")
    ur2 = UR2("UR2")
    
    start_pt_ur1 = V3(287.668457, -68.693909, 331.333344)
    start_pt_ur2 = V3(-287.668457, -68.693909, 331.333344)
    
    #ur1.send_command(move = start_pt_ur1) # 388.6699950049365, -448.746810885241, 582.8156690868195
    ur2.send_command(move = start_pt_ur2) # 374.64720821009803, 452.98348985204194, 577.4463268952555

    