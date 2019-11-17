


def send_cmd_place_block(ur, cmd, deposition_time):
    
    x, y, z, ax, ay, az, acceleration, speed, wait_time = cmd
    
    ur.send_command_movel([x, y, z, ax, ay, az], a=acceleration, v=speed) #init pose
    ur.wait_for_ready() # wait for UR to be ready

    ur.send_command_movel([x, y, z-100, ax, ay, az], a=acceleration, v=speed) #down pose
    ur.wait_for_ready() # wait for UR to be ready

    # turn gripper off    
    ur.send_command_digital_out(0, False) # OPEN valve
    ur.send_command_wait(deposition_time) # wait
    #ur.send_command_wait(0.5)  # wait again

    ur.wait_for_ready() # wait for UR to be ready

    ur.send_command_movel([x, y, z, ax, ay, az], a=acceleration, v=speed) #init pose
    ur.wait_for_ready() # wait for UR to be ready



