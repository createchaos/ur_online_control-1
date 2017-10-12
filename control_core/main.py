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

import ur_online_control.control_core.global_access as global_access
from ur_online_control.control_core.server import Server
from ur_online_control.control_core.wrapper import ClientWrapper

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
    
    #gh = ClientWrapper("GH")
    ur = ClientWrapper("UR")
    
    #gh.wait_for_connected()
    ur.wait_for_connected()
    
    current_pose_cartesian = ur.get_current_pose_cartesian()
    
    print(current_pose_cartesian)
    
    current_pose_joint = ur.get_current_pose_joint()
    
    print(current_pose_joint)
    
    """        
    float_list = gh.wait_for_message()
    ur.send_command(float_list)
    """
    server.close()
    
    print("Please press a key to terminate.")
    junk = sys.stdin.readline()
    print("Close done.")
     
if __name__ == "__main__":
    main()  
    
    
    