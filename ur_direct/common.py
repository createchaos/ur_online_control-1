from __future__ import absolute_import

import os
import socket
from .structure import URCommandScript

__all__ = [
    'is_available',
    'send_script',
    'stop',
    'move_linear',
    'generate_moves_linear',
    'generate_script_pick_and_place_block',
    'airpick_toggle',
    'get_current_pose_cartesian',
    'get_current_pose_joints'
]


def is_available(ip):
    """Ping the network, to check for availability"""
    system_call = "ping -r 1 -n 1 {}".format(ip)
    response = os.system(system_call)
    if response == 0:
        return True
    else:
        return False


def send_script(ip, script, port=30002):
    """Send the script to the UR"""
    try:
        s = socket.create_connection((ip, port), timeout=2)
        s.send(script)
        print("Script sent to %s on port %i" % (ip, port))
        s.close()
    except socket.timeout:
        print("UR with ip %s not available on port %i" % (ip, port))
        raise


def stop(ip, port):
    commands = URCommandScript(ur_ip=ip, ur_port=port)
    commands.start()
    commands.add_line("\tstopl(0.5)")
    commands.end()
    commands.generate()
    commands.send_script()


def move_linear(taa, command, feedback=None, server_ip=None, server_port=None):
    """Script for a single linear movement"""
    script = URCommandScript(server_ip=server_ip, server_port=server_port)
    script.start()
    script.set_tcp(taa)
    script.add_move_linear(command, feedback)
    script.end()
    return script.generate()


def generate_moves_linear(taa, move_commands, feedback=None, server_ip=None, server_port=None):
    script = URCommandScript(server_ip=server_ip, server_port=server_port)
    script.start()
    script.set_tcp(taa)
    [script.add_move_linear(move_command, feedback) for move_command in move_commands]
    script.end()
    return script.generate()


def generate_script_pick_and_place_block(taa, move_commands, feedback=None, vacuum_on=2, vacuum_off=5):
    """Script for multiple linear movements and airpick on and off commands"""
    script = URCommandScript()
    script.start()
    script.add_airpick_commands()
    script.set_tcp(taa)
    for i, command in zip(range(len(move_commands)), move_commands):
        if i == vacuum_on:
            script.airpick_on()
        elif i == vacuum_off:
            script.airpick_off()
        else:
            pass
        script.add_move_linear(command, feedback)
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
    return _get_current_pose("cartesian", tcp, server_ip, server_port, ur_ip, ur_port, send)


def get_current_pose_joints(tcp, server_ip, server_port, ur_ip, ur_port, send=False):
    """Script to obtain the current joint positions"""
    return _get_current_pose("joints", tcp, server_ip, server_port, ur_ip, ur_port, send)


def _get_current_pose(pose_type, tcp, server_ip, server_port, ur_ip, ur_port, send):
    """Script to obtain position"""
    commands = URCommandScript(server_ip=server_ip, server_port=server_port, ur_ip=ur_ip, ur_port=ur_port)
    commands.start()
    commands.set_tcp(tcp)
    pose_type_map = {"cartesian": commands.get_current_position_cartesian,
                     "joints": commands.get_current_position_joints}
    pose_type_map[pose_type](send)
    commands.end()
    script = commands.generate()
    print(script)
    commands.send_script()
    return commands


if __name__ == "__main__":
    server_port = 50001
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
    # program = generate_script_pick_and_place_block(tool_angle_axis, movel_cmds)
    # program = get_current_pose_cartesian(server_ip, server_port, ur_ip, ur_port)
    # program = move_linear(tool_angle_axis, move_command, server_ip=server_ip, server_port=server_port, feedback="Full")
    # program = move_linear(tool_angle_axis, move_command, feedback="UR_only")
    # program = generate_moves_linear(tool_angle_axis, movel_cmds, server_ip=server_ip, server_port=server_port, feedback="Full")
    program = get_current_pose_cartesian(tool_angle_axis, server_ip, server_port, ur_ip, ur_port, send=True)
    # program = get_current_pose_joints(tool_angle_axis, server_ip, server_port, ur_ip, ur_port, send=True)
    print(program)
    print(program.received_messages)
