
from server import SimpleServer
from client_socket import SimpleClientSocket
from msg_identifiers import *

def is_available(ip):
    syscall = "ping -r 1 -n 1 %s"
    response = os.system(syscall % ip)
    if response == 0:
        return True
    else:
        return False