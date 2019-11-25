import sys, os, socket

# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, ".."))
parent_parent_dir = os.path.abspath(os.path.join(parent_dir, ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)
sys.path.append(parent_parent_dir)

from ur_online_control.utilities import read_file_to_string, read_file_to_list
from ur_online_control.ur_direct.utilities import send_script, is_available

UR_SERVER_PORT = 30002

def generate_script_pick_block(pick_up_plane):
    pass

def generate_script_place_block():
    pass

def generate_script_pick_and_place_block(tool_angle_axis, movel_cmds=[]):

    
    script_lines = []

    # move to pick up plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[0]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # move to pick up plane
    x, y, z, ax, ay, az, speed, radius = movel_cmds[1]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # turn vacuum on
    script_lines.append("rq_vacuum_grip(advanced_mode=True, maximum_vacuum=60, minimum_vacuum=10, timeout_ms=10, wait_for_object_detected=True, gripper_socket='1')")
    script_lines.append("sleep(1)")

    # move to pick up plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[2]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # move to current plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[3]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

    # move to current plane
    x, y, z, ax, ay, az, speed, radius = movel_cmds[4]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))

     # turn vacuum off
    script_lines.append("rq_vacuum_release(advanced_mode=True, shutoff_distance_cm=1, wait_for_object_released=True, gripper_socket='1')")
    script_lines.append("sleep(1)")

    # move to current plane safe level
    x, y, z, ax, ay, az, speed, radius = movel_cmds[5]
    script_lines.append("movel(p%s, v=%f, r=%f)" % (str([x/1000., y/1000., z/1000, ax, ay, az]), speed/1000., radius/1000.))


    script = "\n"
    script += "textmsg(\">> program start\")\n"

    x, y, z, ax, ay, az = tool_angle_axis
    script += "set_tcp(p%s)\n" % str([x/1000., y/1000., z/1000, ax, ay, az]) # set tool tcp
    
    script += "".join(["%s\n" % line for line in script_lines])
    script += "textmsg(\"<< program end\")\n"
    script += "end\n"
    script += "prog()\n\n"

    
    path = os.path.join(os.path.dirname(__file__), "scripts")
    methods_file = os.path.join(path, "airpick_methods.script") 
    methods_str = read_file_to_string(methods_file)
    program_str = methods_str + "\n" + script
    return program_str    

def generate_script_airpick_on():

    # the path of the scripts files
    path = os.path.join(os.path.dirname(__file__), "scripts")
    methods_file = os.path.join(path, "airpick_methods.script") 
    methods_str = read_file_to_string(methods_file)
    vacuum_on_file = os.path.join(path, "airpick_vacuum_on.script")
    vacuum_on_str = read_file_to_string(vacuum_on_file)
    program_str = methods_str + "\n" + vacuum_on_str
    return program_str


def generate_script_airpick_off():

    # the path of the scripts files
    path = os.path.join(os.path.dirname(__file__), "scripts")
    methods_file = os.path.join(path, "airpick_methods.script") 
    methods_str = read_file_to_string(methods_file)
    vacuum_off_file = os.path.join(path, "airpick_vacuum_off.script")
    vacuum_off_str = read_file_to_string(vacuum_off_file)
    program_str = methods_str + "\n" + vacuum_off_str
    return program_str

if __name__ == "__main__":
    
    ur_ip = "192.168.10.10"
    #program = generate_script_airpick_on()

    tool_angle_axis = [0,0,0,0,0,0]
    cmd = [0,0,0,0,0,0,0,0]
    movel_cmds=[cmd, cmd, cmd, cmd, cmd, cmd]

    program = generate_script_pick_and_place_block(tool_angle_axis, movel_cmds)
    print(program)

    

    #send_script(ur_ip, program)