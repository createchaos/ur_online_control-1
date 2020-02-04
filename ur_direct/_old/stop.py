from utilities import send_script, is_available

script = ""
script += "def program():\n"
script += "\tstopl(0.5)\n"
script += "\ttextmsg(\"stopped..\")\n"
script += "end\n"
script += "program()\n\n\n"

def stop(ur_ip):

    global script
    print(script)

    ur_available = is_available(ur_ip)

    if ur_available:
        send_script(ur_ip, script)


if __name__ == "__main__":

    ur_ip = "192.168.10.10"
    stop(ur_ip)
