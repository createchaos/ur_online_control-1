import socket
from SocketServer import TCPServer, BaseRequestHandler
#from socketserver import TCPServer, BaseRequestHandler
import sys
import os
# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, ".."))
parent_parent_dir = os.path.abspath(os.path.join(parent_dir, ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)
sys.path.append(parent_parent_dir)
from ur_online_control.utilities import read_file_to_string, read_file_to_list


def list_str_to_list(str):
    str = str[(str.find("[") + 1):str.find("]")]
    return [float(x) for x in str.split(",")]


def is_available(ur_ip):
    system_call = "ping -r 1 -n 1 {}".format(ur_ip)
    response = os.system(system_call)
    if response == 0:
        return True
    else:
        return False


def send_script(ur_ip, script, port=30002):
    try:
        s = socket.create_connection((ur_ip, port), timeout=2)
        s.send(script)
        print("Script sent to %s on port %i" % (ur_ip, port))
        s.close()
    except socket.timeout:
        print("UR with ip %s not available on port %i" % (ur_ip, port))
        raise


class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        pose = ""
        while pose.find("]") == -1:
            pose += self.request.recv(1024)
        self.server.rcv_msg = pose
        self.server.server_close()  # this throws an exception


def move_linear(move_command, tool_angle_axis, feedback=False, server_ip=None, server_port=None):
    script = URCommandScript()
    script.start()
    script.set_tcp(tool_angle_axis)
    script.add_move_linear(move_command, feedback, server_ip, server_port)
    script.end()
    return script.dict_to_script()


def generate_script_pick_and_place_block(tool_angle_axis=[], move_commands=[], vacuum_on=2, vacuum_off=5):
    script = URCommandScript()
    script.start()
    script.add_airpick_commands()
    script.set_tcp(tool_angle_axis)
    for i, move_command in zip(range(len(move_commands)), move_commands):
        if i == vacuum_on:
            script.airpick_on()
        elif i == vacuum_off:
            script.airpick_off()
        else:
            pass
        script.add_move_linear(move_command)
    script.end()
    return script.dict_to_script()


def airpick_toggle(toggle=False):
    script = URCommandScript()
    script.start()
    script.add_airpick_commands()
    if toggle:
        script.airpick_on()
    elif not toggle:
        script.airpick_off()
    script.end()
    return script.dict_to_script()


def get_current_pose_cartesian(server_ip, server_port, ur_ip):
    return get_current_pose("cartesian", server_ip, server_port, ur_ip)


def get_current_pose_joints(server_ip, server_port, ur_ip):
    return get_current_pose("joints", server_ip, server_port, ur_ip)


def get_current_pose(pose_type, server_ip, server_port, ur_ip):
    script = URCommandScript()
    script.start()
    script.set_tcp([0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    pose_type_map = {"cartesian": script.get_current_position_cartesian,
                     "joints": script.get_current_position_joints}
    pose_type_map[pose_type](server_ip, server_port)
    script.end()

    program = script.dict_to_script()

    #return program

    if is_available(ur_ip):
        server = TCPServer((server_ip, server_port), MyTCPHandler)
        send_script(ur_ip, program)
        # send file
        try:
            server.serve_forever()
        except:
            return list_str_to_list(server.rcv_msg)


class URCommandScript:
    def __init__(self):
        self.commands_dict = {}
        self.socket_status = False
        self.server_ip = None
        self.server_port = None
        self.ur_ip = None

    def dict_to_script(self):
        return '\n'.join(self.commands_dict.values())

    def start(self):
        commands = [
            "def program():",
            "\ttextmsg(\">> Entering program.\")",
            "\t# open line for airpick commands"
        ]
        self.add_lines(commands)

    def end(self):
        self.socket_close()
        commands = [
            "\ttextmsg(\"<< Exiting program.\")",
            "end",
            "program()\n\n\n"]
        self.add_lines(commands)

    def add_line(self, line, i=None):
        if i is None:
            i = len(self.commands_dict)
        else:
            pass
        self.commands_dict[i] = line

    def add_lines(self, lines):
        i = len(self.commands_dict)
        [self.add_line(line, i+line_nr) for (line_nr, line) in zip(range(len(lines)), lines)]

    def set_tcp(self, tcp):
        tcp = [tcp[i]/1000 if i < 3 else tcp[i] for i in range(len(tcp))]
        self.add_line("\tset_tcp(p{})".format(tcp))

    def get_current_position_cartesian(self, server_ip, server_port):
        self.socket_open(server_ip, server_port)
        commands = ["\tcurrent_pose = get_forward_kin()",
                    "\ttextmsg(current_pose)",
                    "\tMM2M = 1000.0",
                    "\tsocket_send_string([current_pose[0] * MM2M, current_pose[1] * MM2M, current_pose[2] * MM2M, current_pose[3], current_pose[4], current_pose[5]])"]
        self.add_lines(commands)

    def get_current_position_joints(self, server_ip, server_port):
        self.socket_open(server_ip, server_port)
        commands = ["\tcurrent_pose = get_joint_positions()",
                    "\ttextmsg(current_pose)",
                    "\tsocket_send_string([current_pose[0], current_pose[1], current_pose[2], current_pose[3], current_pose[4], current_pose[5]])"]
        self.add_lines(commands)

    def socket_open(self, server_ip, server_port):
        if not self.socket_status:
            self.add_line('\tsocket_open("{}", {})'.format(server_ip, server_port))
            self.socket_status = True
        else:
            pass

    def socket_close(self):
        if self.socket_status:
            self.add_line("\tsocket_close()")
        else:
            pass

    def add_move_linear(self, move_command, feedback=False, server_ip=None, server_port=None):
        move_command = [cmd / 1000 if c not in [3, 4, 5] else cmd for c, cmd in zip(range(len(move_command)), move_command)]
        [x, y, z, dx, dy, dz, v, r] = move_command
        self.add_line("\tmovel(p[{}, {}, {}, {}, {}, {}], v={}, r={})".format(x, y, z, dx, dy, dz, v, r))
        if feedback:
            self.get_current_position_cartesian(server_ip, server_port)

    def airpick_on(self, max_vac=75, min_vac=25, detect=True):
        self.add_line('\trq_vacuum_grip(advanced_mode=True, maximum_vacuum={}, minimum_vacuum={}, timeout_ms=10, wait_for_object_detected={}, gripper_socket="1")'.format(max_vac, min_vac, detect))

    def airpick_off(self):
        self.add_line('\trq_vacuum_release(advanced_mode=True, shutoff_distance_cm=1, wait_for_object_released=False, gripper_socket="1", pressure = 55, timeout = 55)')

    def add_airpick_commands(self):
        path = os.path.join(os.path.dirname(__file__), "scripts")
        program_file = os.path.join(path, "airpick_methods.script")
        program_str = read_file_to_string(program_file)
        self.add_line(program_str, 2)

    def send_script(self, ur_ip, server_ip, server_port=30002):
        script = self.dict_to_script()

        # start server
        server = TCPServer((server_ip, server_port), MyTCPHandler)

        try:
            s = socket.create_connection((ur_ip, server_port), timeout=2)
            s.send(script)
            print("Script sent to %s on port %i" % (ur_ip, server_port))
            s.close()
        except socket.timeout:
            print("UR with ip %s not available on port %i" % (ur_ip, server_port))
            raise

        # send file
        try:
            server.serve_forever()
        except:
            return list_str_to_list(server.rcv_msg)


if __name__ == "__main__":
    server_port = 30002
    server_ip = "192.168.10.11"
    ur_ip = "192.168.10.20"

    tool_angle_axis = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    move_command = [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0]
    movel_cmds = [
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0],
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0],
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0],
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0],
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0],
        [900.0, 45.0, 25.0, 2.0, -2.0, 0.0, 20.0, 0.0]
    ]
    #program = generate_script_pick_and_place_block(tool_angle_axis, movel_cmds)
    #program = airpick_toggle(True)
    #program = get_current_pose_cartesian(server_ip, server_port, ur_ip)
    program = move_linear(move_command, tool_angle_axis)
    print(program)
