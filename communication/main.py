'''
Created on 22.11.2016
@author: rustr
'''

from __future__ import print_function
import time
import sys
import os

# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, "..", ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)


import ur_online_control.communication.container as container
from ur_online_control.communication.server import Server
from ur_online_control.communication.client_wrapper import ClientWrapper
from ur_online_control.communication.formatting import format_commands

from eggshell_bh.linear_axis import siemens as s

#create logger to debug the code and check the speed and time
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter("%(asctime)s:    %(levelname)s:  %(message)s")

file_handler = logging.FileHandler("main.log")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

if len(sys.argv) > 1:
    server_address = sys.argv[1]
    server_port = int(sys.argv[2])
    ur_ip = sys.argv[3]
    print(sys.argv)
else:
    #server_address = "192.168.10.12"
    server_address = "127.0.0.1"
    server_port = 30003
    #ur_ip = "192.168.10.11"
    ur_ip = "127.0.0.1"


def main():

    logger.info("\n\nlog started ,main is running\n")

    # start the server
    server = Server(server_address, server_port)
    server.start()
    server.client_ips.update({"UR": ur_ip})

    logger.info("server started")

    # create client wrappers, that wrap the underlying communication to the sockets
    gh = ClientWrapper("GH")
    ur = ClientWrapper("UR")

    logger.info("client wrappers created")

    # wait for the clients to be connected
    gh.wait_for_connected()
    ur.wait_for_connected()

    logger.info("gh and ur are connected")

    # now enter fabrication loop
    while True: # and ur and gh connected
        # let gh control if we should continue
        continue_fabrication = gh.wait_for_int()
        print("continue_fabrication: %i" % continue_fabrication)
        if not continue_fabrication:
            break

        move_filament_loading_pt = gh.wait_for_int()
        print("move_filament_loading_pt: %i" % move_filament_loading_pt)

        linear_axis_toggle = gh.wait_for_int()
        print("linear_axis_toggle: %i" % linear_axis_toggle)

        #if linear_axis_toggle:
        axis_moving_pts_indices = gh.wait_for_float_list()
        print("We received %i linear axis_moving_pts_indices" % len(axis_moving_pts_indices))

        logger.info("{} float list of axis_moving_pts_indices received".format(len(axis_moving_pts_indices)))

        #if the ur required to start extruding always from the same start base
        linear_axis_x = 500
        linear_axis_z = 500

        if linear_axis_toggle:
            # And move axis
            p = s.SiemensPortal(2)
            logger.info("siemens portal connected")
            print ("Siemens portal connected")
            currentPosX = p.get_x()
            currentPosZ = p.get_z()
            if currentPosZ != linear_axis_z and currentPosX != linear_axis_x:
                p.set_x(linear_axis_x)
                p.set_z(linear_axis_z)
                print ("Linear axis is set to default x and z value")
                print("Waiting for 10 seconds")
                ur.send_command_wait(10)
            p.close()

        len_command = gh.wait_for_int()
        print("len_command: %i" % len_command)

        no_batches = gh.wait_for_int()
        print("no_batches: %i" % no_batches)

        commands_to_wait_flattened = []

        for j in range(no_batches):
            commands_flattened = gh.wait_for_float_list()
            # create mew list for commands executed
            commands_to_wait_flattened.extend(commands_flattened)
            # the commands are formatted according to the sent length
            commands = format_commands(commands_flattened, len_command)
            print("We received %i commands." % len(commands))
            logger.info("{} float list of commands_flattened received".format(len(commands)))

            if move_filament_loading_pt:
            	commands_to_send = commands
            else:
            	commands_to_send = commands[1:-1]

            for i, cmd in enumerate(commands_to_send):
                 x, y, z, ax, ay, az, speed, radius = cmd
                 ur.send_command_movel([x, y, z, ax, ay, az], v=speed, r=radius)
                 if i %100 == 0:
                     logger.info("command movel number {} is sent".format(i))

                 if move_filament_loading_pt and i == 0:
                     # after Moving to first point, toggle extruder and wait
                     print("Moved to safe point")
                     print("Toggling extruder")
                     ur.send_command_digital_out(0, True)
                     print("Waiting for 30 seconds")
                     ur.send_command_wait(30)

            logger.info("batch number {} was sent".format(j))

        logger.info("all batches were sent")

        commands_2 = format_commands(commands_to_wait_flattened, len_command)
        print("We received %i commands_to_wait." % len(commands_2))
        if move_filament_loading_pt:
        	commands_to_wait = commands_2
        else:
        	commands_to_wait = commands_2[1:-1]

        # move linear axis except start and end (at filament loading and unloading pos)
        linear_axis_move = linear_axis_z
        p1 = s.SiemensPortal(2)
        for i, cmd in enumerate(commands_to_wait):
            if i > 3: #one for send to safe_pt, second for send_command_digital_out, third for send_command_wait
                ur.wait_for_command_executed(i)
                print("Executed command", i+1, "of", len(commands_to_wait), "[", (i+1)*100/(len(commands_to_wait)), "%]")
                if linear_axis_toggle :
                    if i in axis_moving_pts_indices:
                        linear_axis_move += 1
                        p1.set_z(linear_axis_move)
                        print ("Linear axis moved to %d mm"%linear_axis_move)
                        print ("Linear axis moved at point index %d"%i)
                        logger.info("Linear axis moved to {} mm".format(linear_axis_move))
                 #     current_pose_cartesian = ur.get_current_pose_cartesian()
                 #     print(current_pose_cartesian)


        logger.info("before wait_for_ready")
        ur.wait_for_ready()
        logger.info("after wait_for_ready")
        ur.send_command_digital_out(0, False)
        gh.send_float_list(commands[0])
        print("============================================================")

    p1.close()
    ur.quit()
    gh.quit()
    server.close()

    logger.info("siemens protal, gh, ur and server are closed")

    print("Please press a key to terminate the program.")
    junk = sys.stdin.readline()
    print("Done.")

if __name__ == "__main__":
    main()
