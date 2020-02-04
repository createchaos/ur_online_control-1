import socket
import sys
import os
import time
import threading
# set the paths to find library
file_dir = os.path.dirname( __file__)
parent_dir = os.path.abspath(os.path.join(file_dir, ".."))
parent_parent_dir = os.path.abspath(os.path.join(parent_dir, ".."))
sys.path.append(file_dir)
sys.path.append(parent_dir)
sys.path.append(parent_parent_dir)

if sys.version_info[0] == 2:
    from SocketServer import TCPServer, ThreadingMixIn, BaseRequestHandler
elif sys.version_info[0] == 3:
    from socketserver import TCPServer, ThreadingMixIn, BaseRequestHandler

def list_str_to_list(str):
    str = str[(str.find("[") + 1):str.find("]")]
    return [float(x) for x in str.split(",")]

def read_file_to_string(afile):
    with open(afile) as f:
        afile_str = f.read()
    return afile_str


def is_available(ur_ip):
    """Ping the network, to check for availability"""
    system_call = "ping -r 1 -n 1 {}".format(ur_ip)
    response = os.system(system_call)
    if response == 0:
        return True
    else:
        return False


def send_script(ur_ip, script, port=30002):
    """Send the script to the UR"""
    try:
        s = socket.create_connection((ur_ip, port), timeout=2)
        s.send(script)
        print("Script sent to %s on port %i" % (ur_ip, port))
        s.close()
    except socket.timeout:
        print("UR with ip %s not available on port %i" % (ur_ip, port))
        raise


def wait_for_message(server, message, ur_ip, script, port=30002, timeout=1000):
    t0 = time.time()
    t1 = t0
    while (t1-t0) < timeout:
        t1 = time.time()
        if server.rcv_msg == message:
            send_script(ur_ip, script, port)
            print("Script sent after message received")
            break
        else:
            pass
    print("No identical message found, timeout reached")


class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(1024)
        data = data.decode('utf-8')
        data = data.split('\n')
        self.server.rcv_msg = data

class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass


def stop(ur_ip, ur_port):
    commands = URCommandScript(ur_ip=ur_ip, ur_port=ur_port)
    commands.start()
    commands.add_line("\tstopl(0.5)")
    commands.end()
    commands.generate()
    commands.send_script()


def move_linear(tool_angle_axis, move_command, feedback=None, server_ip=None, server_port=None):
    """Script for a single linear movement"""
    script = URCommandScript(server_ip=server_ip, server_port=server_port)
    script.start()
    script.set_tcp(tool_angle_axis)
    script.add_move_linear(move_command, feedback)
    script.end()
    return script.generate()


def generate_moves_linear(tool_angle_axis, move_commands, feedback=None, server_ip=None, server_port=None):
    script = URCommandScript(server_ip=server_ip, server_port=server_port)
    script.start()
    script.set_tcp(tool_angle_axis)
    [script.add_move_linear(move_command, feedback) for move_command in move_commands]
    script.end()
    return script.generate()


def generate_script_pick_and_place_block(tool_angle_axis, move_commands, vacuum_on=2, vacuum_off=5):
    """Script for multiple linear movements and airpick on and off commands"""
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
    return script.generate()


def airpick_toggle(toggle=False, max_vac=75, min_vac=25, detect=True, pressure=55, timeout=55):
    """Script to toggle the airpick on/off"""
    script = URCommandScript()
    script.start()
    script.add_airpick_commands()
    if toggle:
        script.airpick_on(max_vac, min_vac, detect)
    elif not toggle:
        script.airpick_off(pressure, timeout)
    script.end()
    return script.generate()


def get_current_pose_cartesian(tcp, server_ip, server_port, ur_ip, ur_port, send=False):
    """Script to obtain the current cartesian coordinates"""
    return get_current_pose("cartesian", tcp, server_ip, server_port, ur_ip, ur_port, send)


def get_current_pose_joints(tcp, server_ip, server_port, ur_ip, ur_port, send=False):
    """Script to obtain the current joint positions"""
    return get_current_pose("joints", tcp, server_ip, server_port, ur_ip, ur_port, send)


def get_current_pose(pose_type, tcp, server_ip, server_port, ur_ip, ur_port, send):
    """Script to obtain position"""
    commands = URCommandScript(server_ip=server_ip, server_port=server_port, ur_ip=ur_ip, ur_port=ur_port)
    commands.start()
    commands.set_tcp(tcp)
    pose_type_map = {"cartesian": commands.get_current_position_cartesian,
                     "joints": commands.get_current_position_joints}
    pose_type_map[pose_type](send)
    commands.end()
    commands.generate()
    return commands.send_script()

class URCommandScript:
    """Class containing commands for the UR Robot system"""
    def __init__(self, server_ip=None, server_port=None, ur_ip=None, ur_port=None):
        self.commands_dict = {}
        self.socket_status = False
        self.server_ip = server_ip
        self.server_port = server_port
        self.ur_ip = ur_ip
        self.ur_port = ur_port
        self.received_messages = {}

    def generate(self):
        """Translate the dictionary to a long string"""
        self.script = '\n'.join(self.commands_dict.values())
        return self.script

    def start(self):
        """To build the start of the script"""
        commands = [
            "def program():",
            "\ttextmsg(\">> Entering program.\")",
            "\t# open line for airpick commands"
        ]
        self.add_lines(commands)

    def end(self):
        """To build the end of the script"""
        self.socket_close()
        commands = [
            "\ttextmsg(\"<< Exiting program.\")",
            "end",
            "program()\n\n\n"]
        self.add_lines(commands)

    def add_line(self, line, i=None):
        """Add a single line to the script"""
        if i is None:
            i = len(self.commands_dict)
        else:
            pass
        self.commands_dict[i] = line

    def add_lines(self, lines):
        """Add a multiple lines to the script"""
        i = len(self.commands_dict)
        [self.add_line(line, i+line_nr) for (line_nr, line) in zip(range(len(lines)), lines)]

    def set_tcp(self, tcp):
        """Set the tcp"""
        tcp = [tcp[i]/1000 if i < 3 else tcp[i] for i in range(len(tcp))]
        self.add_line("\tset_tcp(p{})".format(tcp))

    def get_current_position_cartesian(self, send=False):
        """Get the current cartesian position"""
        self.get_current_pose("cartesian", send)

    def get_current_position_joints(self, send=False):
        """Get the current joints positions"""
        self.get_current_pose("joints", send)

    def get_current_pose(self, get_type, send):
        """Create get position code"""
        pose_type = {
            "cartesian": "get_actual_tcp_pose()",
            "joints": "get_actual_joint_positions()"
        }
        commands = ["\tcurrent_pose = {}".format(pose_type[get_type]),
                    "\ttextmsg(current_pose)"]
        self.add_lines(commands)
        if send:
            self.socket_open()
            self.add_line("\tsocket_send_string(current_pose)")

        else:
            pass

    def socket_open(self):
        """Open socket for communication outside of the UR script"""
        if not self.socket_status:
            self.add_line('\tsocket_open("{}", {})'.format(self.server_ip, self.server_port))
            self.socket_status = True
        else:
            pass

    def socket_close(self):
        """Close the socket"""
        if self.socket_status:
            self.add_line('\ttextmsg("Closing the socket")')
            self.add_line('\tsocket_send_string("\n[Done]")')
            self.add_line("\tsocket_close()")
        else:
            pass

    def add_move_linear(self, move_command, feedback=None):
        """Add a move command to the script"""
        move = [cmd / 1000 if c not in [3, 4, 5] else cmd for c, cmd in zip(range(len(move_command)), move_command)]
        [x, y, z, dx, dy, dz, v, r] = move
        self.add_line("\tmovel(p[{}, {}, {}, {}, {}, {}], v={}, r={})".format(x, y, z, dx, dy, dz, v, r))
        if feedback == "Full":
            self.get_current_position_cartesian(True)
        elif feedback == "UR_only":
            self.get_current_position_cartesian(False)
        else:
            pass

    def airpick_on(self, max_vac=75, min_vac=25, detect=True):
        """Turn airpick on"""
        self.add_line('\trq_vacuum_grip(advanced_mode=True, maximum_vacuum={}, minimum_vacuum={}, timeout_ms=10, wait_for_object_detected={}, gripper_socket="1")'.format(max_vac, min_vac, detect))

    def airpick_off(self, pressure=100, timeout=25):
        """Turn airpick off"""
        self.add_line('\trq_vacuum_release(advanced_mode=True, shutoff_distance_cm=1, wait_for_object_released=True, gripper_socket="1", pressure = {}, timeout = {})'.format(pressure, timeout))
        self.add_line("\tsleep(0.1)")

    def add_airpick_commands(self):
        """Add airpick functionality to the script"""
        path = os.path.join(os.path.dirname(__file__), "scripts")
        program_file = os.path.join(path, "airpick_methods.script")
        program_str = read_file_to_string(program_file)
        self.add_line(program_str, 2)

    def is_available(self):
        """Ping the network, to check for availability"""
        system_call = "ping -r 1 -n 1 {}".format(self.ur_ip)
        response = os.system(system_call)
        if response == 0:
            return True
        else:
            return False

    def transmit(self):
        try:
            s = socket.create_connection((self.ur_ip, self.ur_port), timeout=2)
            script_send = self.script.encode('utf-8')
            s.send(script_send)
            print("Script sent to {} on port {}".format(self.ur_ip, self.ur_port))
            s.close()
        except socket.timeout:
            print("UR with ip {} not available on port {}".format(self.ur_ip, self.ur_port))
            raise

    def add_message(self, message):
        i = len(self.received_messages)
        self.received_messages[i] = message

    def send_script(self):
        """Transmit the script to the UR robot"""
        if self.is_available:
            if self.socket_status:
                # start server
                server = ThreadedTCPServer((self.server_ip, self.server_port), MyTCPHandler)
                ip, port = server.server_address
                server_thread = threading.Thread(target=server.serve_forever)
                server_thread.daemon = True
                server_thread.start()
                print("Server loop running in thread:", server_thread.name)
                print("IP: {}, PORT: {}".format(ip, port))
                # send file
                server.rcv_msg = None
                self.transmit()
                while "[Done]" not in self.received_messages.values():
                    if server.rcv_msg is None:
                        pass
                    elif type(server.rcv_msg) == list:
                        [self.add_message(i) for i in server.rcv_msg if i not in self.received_messages.values()]
                        print(self.received_messages)
                    elif server.rcv_msg is not None and type(server.rcv_msg) != list and server.rcv_msg not in self.received_messages.values():
                        self.add_message(server.rcv_msg)
                        print(self.received_messages)
                    else:
                        pass
                server.shutdown()
                server.server_close()
                return self.received_messages
            else:
                self.transmit()
        else:
            pass

if __name__ == "__main__":
    server_port = 50003
    server_ip = "192.168.10.11"
    ur_ip = "192.168.10.20"
    ur_port = 30002

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
    #program = get_current_pose_cartesian(server_ip, server_port, ur_ip, ur_port)
    #program = move_linear(tool_angle_axis, move_command, server_ip=server_ip, server_port=server_port, feedback="Full")
    #program = move_linear(tool_angle_axis, move_command, feedback="UR_only")
    #program = generate_moves_linear(tool_angle_axis, movel_cmds, server_ip=server_ip, server_port=server_port, feedback="Full")
    #program = get_current_pose_cartesian(tool_angle_axis, server_ip, server_port, ur_ip, ur_port, send=True)
    program = get_current_pose_joints(tool_angle_axis, server_ip, server_port, ur_ip, ur_port, send=True)
    print(program)
