


def send_cmd_place_sand(ur, deposition_time):
    
    ur.send_command_digital_out(0, True) # OPEN valve
    # wait
    ur.send_command_wait(deposition_time)
    # turn sand off
    ur.send_command_digital_out(0, False) # CLOSE valve
    # wait again
    ur.send_command_wait(0.5)



