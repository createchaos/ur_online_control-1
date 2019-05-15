from __future__ import print_function
from __future__ import absolute_import

import time
import sys
import os
import json

UR_SERVER_PORT = 30002

# set the paths to find library
path = os.path.dirname(__file__)
lib_dir = os.path.abspath(os.path.join(path, "..", ".."))
sys.path.append(lib_dir)

from ur_online_control.communication.formatting import format_commands
from ur_online_control.communication.server import SimpleServer
from ur_online_control.communication.server import MSG_MOVEL
from ur_online_control.communication.server import MSG_QUIT
from ur_online_control.ur_direct import send_script
from ur_online_control.ur_direct import start_extruder_script
from ur_online_control.ur_direct import stop_extruder_script
from ur_online_control.ur_driver import URDriver_3Dprint

# GLOBALS 
# ===============================================================
server_address = "192.168.10.2"
#server_address = "127.0.0.1"
server_port = 30003
ur_ip = "192.168.10.13"
#ur_ip = "127.0.0.1"
tool_angle_axis = [-68.7916, -1.0706, 264.9818, 3.1416, 0.0, 0.0]
# ===============================================================

# COMMANDS
# ===============================================================
filename = os.path.join(path, "..", "commands.json")
with open(filename, 'r') as f:
    data = json.load(f)
# load the commands from the json dictionary
move_filament_loading_pt = data['move_filament_loading_pt']
linear_axis_toggle = data['move_linear_axis']
axis_moving_pts_indices = data['axis_moving_pts_indices']
len_command = data['len_command']
gh_commands = data['gh_commands']
commands = format_commands(gh_commands, len_command)
print("We have %d commands to send" % len(commands))
# ===============================================================

def main(commands):

    if move_filament_loading_pt:
        first_command = commands[0]
        last_command = commands[-1]
        script = start_extruder_script(tool_angle_axis, first_command)
        send_script(ur_ip, script)
        time.sleep(60)
    
    commands = commands[1:-1]
    #commands = commands[:20]

    # start server
    server = SimpleServer(server_address, server_port)
    server.start()
    
    # send driver to connect
    ur_driver = URDriver_3Dprint(server_address, server_port, tool_angle_axis, ur_ip)
    ur_driver.send()

    # wait until connected
    while not len(server.clients):
        time.sleep(0.5)
    print("UR is connected.")

    ur_socket = server.clients[0]

    # put all cmds on the snd queue
    acc = 0
    t = 0
    for cmd in commands:
        x, y, z, ax, ay, az, speed, radius = cmd
        cmd = [x, y, z, ax, ay, az, acc, speed, radius, t]
        ur_socket.snd_queue.put((MSG_MOVEL, cmd))
    
    # first send 5 commands, the rest is handled by the client
    batch_size = 5
    print("Sending the first %d movel commands." % batch_size)
    for i in range(batch_size):
        msg_id, cmd = ur_socket.snd_queue.get()
        ur_socket.send(msg_id, cmd)

    # wait for all done
    current_counter = 0
    while ur_socket.counter < len(commands):
        time.sleep(0.1)
        if current_counter != ur_socket.counter:
            current_counter = ur_socket.counter
            print("Waiting... executed %d of %d" % (current_counter, len(commands)))
        #if current_counter >= len(commands) - 1000:
        #    # send email
    
    print("Done.")

    # Terminate ur and server
    ur_socket.send(MSG_QUIT)
    server.close()
    
    if move_filament_loading_pt:
        script = stop_extruder_script(tool_angle_axis, last_command)
        send_script(ur_ip, script)
        time.sleep(1)


def only_send_driver():
    # send driver to connect
    ur_driver = URDriver_3Dprint(server_address, server_port, tool_angle_axis, ur_ip)
    ur_driver.send()

if __name__ == "__main__":
    main(commands)
