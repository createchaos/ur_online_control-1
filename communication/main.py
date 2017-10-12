'''
Created on 22.11.2016

@author: rustr
'''
from __future__ import print_function
import time
import sys
import os

# set the paths
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, "..", ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)

import ur_online_control.communication.global_access as global_access
from ur_online_control.communication.server import Server
from ur_online_control.communication.client_wrapper import ClientWrapper
from ur_online_control.communication.formatting import format_commands

if len(sys.argv) > 1:
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    ur_ip = sys.argv[3]
    print(sys.argv)
else:
    server_address = "192.168.10.12"
    server_port = 30003
    ur_ip = "192.168.10.11"


def main():
            
    # start the server
    server = Server(server_address, server_port)
    server.start()
    server.client_ips.update({"UR": ur_ip})
    
    # create client wrappers, that wrap the underlying communication to the sockets
    gh = ClientWrapper("GH")
    ur = ClientWrapper("UR")
    
    # wait for the clients to be connected
    gh.wait_for_connected()
    #ur.wait_for_connected()
    
    msg_float_list = gh.wait_for_float_list()
    print(msg_float_list)
    
    # now enter fabrication loop
    while True:
        # let gh control if we should continue
        continue_fabrication = gh.wait_for_int()
        if not continue_fabrication:
            break
        msg_float_list = gh.wait_for_float_list()
        # we know this are commands, so we format them accordingly
        commands = format_commands(msg_float_list)
        for cmd in commands:
            ur.send_command(cmd)
        ur.wait_for_ready()
        # wait for sensor value
        digital_in = ur.wait_for_digital_in()
        current_pose_joint = ur.wait_for_current_pose_joint()
        current_pose_cartesian = ur.get_current_pose_cartesian()
        # send further to gh
        gh.send_float_list(digital_in)
        gh.send_float_list(current_pose_joint)
        gh.send_float_list(current_pose_cartesian)
        
    server.close()
    
    print("Please press a key to terminate the program.")
    junk = sys.stdin.readline()
    print("Done.")
     
if __name__ == "__main__":
    main()  
    
    
    