from SocketServer import TCPServer, BaseRequestHandler
from utilities import send_script, is_available

script = ""
script += "def program():\n"
script += "\ttextmsg(\">> Entering program.\")\n"
script += "\tSERVER_ADDRESS = \"{SERVER_ADDRESS}\"\n"
script += "\tPORT = {PORT}\n"
script += "\ttextmsg(SERVER_ADDRESS)\n"
script += "\ttextmsg(PORT)\n"
script += "\tset_tcp(p{TCP})\n"
script += "\tMM2M = 1000.0\n"
script += "\tsocket_open(SERVER_ADDRESS, PORT)\n"

script += "\tmovel(p[-0.94920865760722839, -0.7210000000126604, 0.15530000000698363, 2.2214414690791879, -2.2214414690791782, 2.1090559403470218e-15], v=0.10000, r=0.020000)\n"
script += "\tmovel(p[-0.94920865760722817, -0.7210000000126604, -0.034699999993016359, 2.2214414690791879, -2.2214414690791782, 2.1090559403470218e-15], v=0.10000, r=0.000000)\n"
script += "\tmovel(p[-0.94920865760722839, -0.7210000000126604, 0.15530000000698363, 2.2214414690791879, -2.2214414690791782, 2.1090559403470218e-15], v=0.10000, r=0.020000)\n"
script += "\tmovel(p[-0.88557122466850502, -0.048453008156628473, 0.15530000000698377, 2.7608853849878274, -1.4990384558275929, 2.4793098749091016e-15], v=0.10000, r=0.020000)\n"
script += "\tmovel(p[-0.8855712246685048, -0.048453008156628473, 0.035300000006983766, 2.7608853849878274, -1.4990384558275929, 2.4793098749091016e-15], v=0.10000, r=0.000000)\n"
script += "\tmovel(p[-0.88557122466850502, -0.048453008156628473, 0.15530000000698377, 2.7608853849878274, -1.4990384558275929, 2.4793098749091016e-15], v=0.10000, r=0.000000)\n"
script += "\tcurrent_pose = get_forward_kin()\n"
script += "\ttextmsg(current_pose)\n"
script += "\tsocket_send_string([current_pose[0] * MM2M, current_pose[1] * MM2M, current_pose[2] * MM2M, current_pose[3], current_pose[4], current_pose[5]])\n"

script += "\tsocket_close()\n"
script += "\ttextmsg(\"<< Exiting program.\")\n"
script += "end\n"
script += "program()\n\n\n"


def list_str_to_list(str):
    str = str[(str.find("[")+1):str.find("]")]
    return [float(x) for x in str.split(",")]


class MyTCPHandler(BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        pose = ""
        while pose.find("]") == -1:
            pose += self.request.recv(1024)
        self.server.rcv_msg = pose
        self.server.server_close() # this throws an exception
    

def send_movel_script_feedback(server_ip, server_port, ur_ip, tool_angle_axis, cmd):

    #cmdx, cmdy, cmdz, cmdax, cmday, cmdaz, cmdspeed, cmdradius = cmd

    global script
    script = script.replace("{SERVER_ADDRESS}", server_ip)
    script = script.replace("{PORT}", str(server_port))
    script = script.replace("{TCP}", str([tool_angle_axis[i] if i >= 3 else tool_angle_axis[i]/1000. for i in range(len(tool_angle_axis))]))
    #script = script.replace("{MOVEL}", str([cmdx/1000., cmdy/1000., cmdz/1000, cmdax, cmday, cmdaz]), cmdspeed/1000., cmdradius/1000.)
    script = script.replace("{MOVEL}", str(cmd))

    print(script)

    ur_available = is_available(ur_ip)

    if ur_available:
        # start server
        server = TCPServer((server_ip, server_port), MyTCPHandler)

        send_script(ur_ip, script)
        # send file
        try:
            server.serve_forever()
        except:
            return list_str_to_list(server.rcv_msg)

if __name__ == "__main__":
    server_port = 30005
    server_ip = "192.168.10.11"
    ur_ip = "192.168.10.20"
    tool_angle_axis = [0.0, -2.8878212124549687e-11, 158.28878352076936, 0.0, 0.0, 0.0]
    cmd = [-732.65894179570478, 39.681051056994988, 25.300000006984046, 2.6786480764904135, -1.6414776524228298, 2.3172525411999358e-15, 20, 0]

    pose = generate_movel_script_feedback(server_ip, server_port, ur_ip, tool_angle_axis, cmd)
   
    print("pose", pose)
