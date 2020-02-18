from __future__ import absolute_import

import socket
import os
from .mixins.server_mixins import ServerMixins
from .mixins.airpick_mixins import AirpickMixins

__all__ = [
    'URCommandScript'
]


class URCommandScript(AirpickMixins, ServerMixins):
    """Class containing commands for the UR Robot system"""
    def __init__(self, server_ip=None, server_port=None, ur_ip=None, ur_port=None):
        self.commands_dict = {}
        self.server_ip = server_ip
        self.server_port = server_port
        self.ur_ip = ur_ip
        self.ur_port = ur_port
        self.script = None

        self.feedback = False
        self.server_thread = None
        self.server_started = False
        self.server = None
        self.received_messages = {}
        self.checked_messages = 0
        self.exit_message = "Done"

        # Functionality
    def start(self):
        """To build the start of the script"""
        self.add_lines(["def program():",
                        "\ttextmsg(\">> Entering program.\")",
                        "\t# open line for airpick commands"])

    def end(self):
        """To build the end of the script"""
        if self.feedback:
            self.socket_send_line('"Done"')
        self.add_lines(["\ttextmsg(\"<< Exiting program.\")",
                        "end",
                        "program()\n\n\n"])

    def generate(self):
        """Translate the dictionary to a long string"""
        self.script = '\n'.join(self.commands_dict.values())
        return self.script

    def socket_send_line(self, line):
        self.add_lines(['\tsocket_open("{}", {})'.format(self.server_ip, self.server_port),
                        '\tsocket_send_line({})'.format(line),
                        "\tsocket_close()"])

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
            "cartesian": "get_forward_kin()",
            "joints": "get_actual_joint_positions()"
        }
        self.add_lines(["\tcurrent_pose = {}".format(pose_type[get_type]),
                        "\ttextmsg(current_pose)"])
        if send:
            self.socket_send_line('current_pose')

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
        except socket.timeout:
            print("UR with ip {} not available on port {}".format(self.ur_ip, self.ur_port))
            raise
        finally:
            enc_script = self.script.encode('utf-8')
            s.send(enc_script)
            print("Script sent to {} on port {}".format(self.ur_ip, self.ur_port))
            s.close()

    def send_script(self, feedback=None, server=None):
        """Transmit the script to the UR robot"""
        if feedback:
            self.feedback = feedback
        if self.is_available:
            if self.feedback:
                self.get_server(server)
                self.transmit()
                print("Waiting...")
                self.server_listen()
                print(self.received_messages)
            else:
                self.transmit()
            return True
        else:
            return False

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
