from __future__ import absolute_import

import socket
import os
from .server import start_server, stop_server
from .mixins.airpick_mixins import AirpickMixins

__all__ = [
    'URCommandScript'
]


class URCommandScript(AirpickMixins):
    """Class containing commands for the UR Robot system"""
    def __init__(self, server_ip=None, server_port=None, ur_ip=None, ur_port=None):
        self.commands_dict = {}
        self.socket_status = False
        self.server_ip = server_ip
        self.server_port = server_port
        self.ur_ip = ur_ip
        self.ur_port = ur_port
        self.script = None
        self.received_messages = {}

    # Functionality
    def start(self):
        """To build the start of the script"""
        commands = [
            "def program():",
            "\ttextmsg(\">> Entering program.\")",
            "\t# open line for airpick commands"]
        self.add_lines(commands)

    def end(self):
        """To build the end of the script"""
        self.socket_close()
        commands = [
            "\ttextmsg(\"<< Exiting program.\")",
            "end",
            "program()\n\n\n"]
        self.add_lines(commands)

    def generate(self):
        """Translate the dictionary to a long string"""
        self.script = '\n'.join(self.commands_dict.values())
        return self.script

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
            commands = [
                '\tsocket_send_string("\nDone")',
                "\tsocket_close()"]
            self.add_lines(commands)
        else:
            pass

    # Dictionary building
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

    # Feedback functionality
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
            self.add_line(
                "\tsocket_send_string(current_pose)")
        else:
            pass

    # Connectivity
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
            enc_script = self.script.encode('utf-8')
            s.send(enc_script)
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
                server = start_server(self.server_ip, self.server_port)
                self.transmit()
                while "Done" not in self.received_messages.values():
                    if server.rcv_msg is None:
                        pass
                    elif type(server.rcv_msg) == list:
                        [self.add_message(i) for i in server.rcv_msg if i not in self.received_messages.values()]
                        print(self.received_messages)
                    elif server.rcv_msg is not None and type(
                            server.rcv_msg) != list and server.rcv_msg not in self.received_messages.values():
                        self.add_message(server.rcv_msg)
                        print(self.received_messages)
                    else:
                        pass
                stop_server(server)
                return self.received_messages
            else:
                self.transmit()
        else:
            pass

    # Geometric effects
    def set_tcp(self, tcp):
        """Set the tcp"""
        tcp = [tcp[i]/1000 if i < 3 else tcp[i] for i in range(len(tcp))]
        self.add_line("\tset_tcp(p{})".format(tcp))

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
