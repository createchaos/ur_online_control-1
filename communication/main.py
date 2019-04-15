'''
Created on 22.11.2016
@author: rustr

modified on 07.03.2019
@author: nizar taha
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
        print("============================================================")
        print("continue_fabrication: %i" % continue_fabrication)
        logger.info("continue_fabrication: {}".format(continue_fabrication))

        if not continue_fabrication:
            break

        move_filament_loading_pt = gh.wait_for_int()
        print("move_filament_loading_pt: %i" % move_filament_loading_pt)
        logger.info("move_filament_loading_pt: {}".format(move_filament_loading_pt))

        linear_axis_toggle = gh.wait_for_int()
        print("linear_axis_toggle: %i" % linear_axis_toggle)
        logger.info("linear_axis_toggle: {}".format(linear_axis_toggle))

        #if linear_axis_toggle:
        axis_moving_pts_indices = gh.wait_for_float_list()
        print("We received %i linear axis_moving_pts_indices" % len(axis_moving_pts_indices))
        logger.info("{} float list of axis_moving_pts_indices received".format(len(axis_moving_pts_indices)))

        #if the ur required to start extruding always from the same start base
        print("============================================================")
        linear_axis_x = 500
        linear_axis_z = 800

        if linear_axis_toggle:
            # And move axis
            p = s.SiemensPortal(2)
            logger.info("siemens portal connected")
            currentPosX = p.get_x()
            currentPosZ = p.get_z()
            if currentPosZ != linear_axis_z or currentPosX != linear_axis_x:
                p.set_x(linear_axis_x)
                p.set_z(linear_axis_z)
                print ("Linear axis is set to default x and z value")
                p.wait_ext_axis()
            p.close()

        print("============================================================")
        len_command = gh.wait_for_int()
        print("len_command: %i" % len_command)

        batches_number = gh.wait_for_int()
        print("batches_number: %i" % batches_number)

        # create a list to store commands and use it for commands executed loop
        commands_to_wait_flattened = []
        print("============================================================")
        # loop through all commands batches
        for j in range(batches_number):
            commands_flattened = gh.wait_for_float_list()
            # create mew list for commands executed
            commands_to_wait_flattened.extend(commands_flattened)
            # the flattened commands are formatted according to the sent list length
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

                 if move_filament_loading_pt and i == 0 and j == 0:
                     # after Moving to first point, toggle extruder and wait
                     print("Moved to safe point")
                     print("Toggling extruder")
                     ur.send_command_digital_out(0, True)
                     print("Waiting for 50 seconds")
                     ur.send_command_wait(50)

            print("all commands in batch number %i were sent." %j)
            logger.info("all commands in batch number {} were sent".format(j))

        print("all %i batches were sent." %batches_number)
        logger.info("all {} batches were sent".format(batches_number))

        commands_2 = format_commands(commands_to_wait_flattened, len_command)
        print("We received %i commands_to_wait." % len(commands_2))
        if move_filament_loading_pt:
        	commands_to_wait = commands_2
        else:
        	commands_to_wait = commands_2[1:-1]

        # move linear axis except start and end (at filament loading and unloading pos)
        linear_axis_move_z = linear_axis_z
        linear_axis_failed = False
        print("============================================================")
        p1 = s.SiemensPortal(2)
        for i, cmd in enumerate(commands_to_wait):
            if i > 3: #one for send to safe_pt, second for send_command_digital_out, third for send_command_wait
                ur.wait_for_command_executed(i)
                print("Executed command {} of {} [{}%]".format(i+1, len(commands_to_wait), (i+1)*100/(len(commands_to_wait)) ))
                if linear_axis_toggle :
                    if i in axis_moving_pts_indices:
                        linear_axis_move_z += 1
                        p1.set_z(linear_axis_move_z)
                        print ("Linear axis is supposed to move to %d mm"%linear_axis_move_z)
                        ''' sleeping time depends on linear axis override speed
                        for ex. 0.5 sec sleep is not enough to move 16mm in z
                        '''
                        time.sleep(.7)
                        linear_axis_currentPosZ = p1.get_z()
                        if linear_axis_move_z == linear_axis_currentPosZ:
                            print ("SUCCESS")
                            print ("Linear axis moved to %d mm"%linear_axis_currentPosZ)
                            print ("Linear axis moved at point index %d"%i)
                            logger.info("SUCCESS")
                            logger.info("Linear axis moved to {} mm".format(linear_axis_currentPosZ))
                            logger.info("Executed command {} of {} [{}%]".format(i+1, len(commands_to_wait), (i+1)*100/(len(commands_to_wait)) ))
                        else:
                            print("============================================================")
                            print ("FAILED")
                            print ("Linear axis still at %d mm"%linear_axis_currentPosZ)
                            print ("Linear axis failed to move at point index %d"%i)
                            logger.info("FAILED")
                            logger.info("Linear axis still at {} mm".format(linear_axis_currentPosZ))
                            logger.info("Executed command {} of {} [{}%]".format(i+1, len(commands_to_wait), (i+1)*100/(len(commands_to_wait)) ))

                            ur.purge_commands()
                            print("00_purge done")
                            print("waiting for ready ......... ")
                            ur.wait_for_ready()
                            print("01_send new commands")
                            # toggle extruder, turn off motor
                            ur.send_command_digital_out(0, False)
                            logger.info("02_Nozzle Motor Stopped")
                            print ("02_Nozzle Motor Stopped")
                            # move away robot problem: it still sends it at end
                            x1, y1, z1, ax1, ay1, az1, speed1, radius1 = commands_to_wait[0]
                            ur.send_command_movel([x1, y1, z1, ax1, ay1, az1], v=speed1, r=radius1)
                            print("03_Moving robot to a safe point")
                            logger.info("03_Moving robot to a safe point")
                            print("waiting for ready ......... ")
                            ur.wait_for_ready()
                            linear_axis_failed = True
                            ur.quit()
                            print("04_ur quit")
                            logger.info("04_ur quit")
                            break

        if linear_axis_failed:
            gh.quit()
            print("============================================================")
            break
        else:
            print("============================================================")
            ur.wait_for_ready()
            print("waiting for ready")
            ur.send_command_digital_out(0, False)
            logger.info("nozzle motor stopped")
            print ("Nozzle Motor Stopped")
            gh.send_float_list(commands[0])
            ur.wait_for_ready()
            logger.info("all commands were successfully executed")
            print ("all commands were successfully executed")
            print("============================================================")
            ur.quit()
            gh.quit()
            break

    p1.close()
    time.sleep(1)
    server.close()
    print("siemens protal, gh, ur and server are closed")
    logger.info("siemens protal, gh, ur and server are closed")

    print("Please press a key to terminate the program.")
    junk = sys.stdin.readline()
    print("Done.")

if __name__ == "__main__":
    main()
