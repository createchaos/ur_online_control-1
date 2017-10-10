'''
Created on 20.01.2015

@author: rustr
'''

import globals
from globals.useful_functions import clamp
import socket
import time

UR_SERVER_PORT = 30002

#===============================================================================
def send_stop_to_ur_robot(identifier):
    obj = globals.CLIENT_OBJECTS.get(identifier)
    ip = obj.sender_ip
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, UR_SERVER_PORT))
    s.send("stopl(0.1)\n\n")
    s.close()
    print "Sent STOP to %s on ip %s." % (identifier, ip) 
#===============================================================================
def send_speed_to_ur_robot(identifier, speed, max_speed):
    obj = globals.CLIENT_OBJECTS.get(identifier)
    ip = obj.sender_ip
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ts = time.time()
    s.connect((ip, UR_SERVER_PORT)) # this takes a lot of time sometimes!!! 3 seconds!!!
    print "%s send_speed_to_ur_robot connect" % identifier, time.time() - ts
    speed = speed/float(max_speed)
    speed = clamp(speed, 0.0, 1.0) # clamp speed between 0 and 1
    s.send("set speed %f\n\n" % speed)
    s.close()
#================================= ==============================================