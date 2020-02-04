from __future__ import absolute_import

import sys
import threading
if sys.version_info[0] == 2:
    from SocketServer import TCPServer, ThreadingMixIn, BaseRequestHandler
elif sys.version_info[0] == 3:
    from socketserver import TCPServer, ThreadingMixIn, BaseRequestHandler


__all__ = [
    'MyTCPHandler',
    'ThreadedTCPServer',
    'start_server',
    'stop_server'
]


class MyTCPHandler(BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        data = self.request.recv(1024)
        data = data.decode('utf-8')
        data = data.split('\n')
        self.server.rcv_msg = data


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    pass


def start_server(server_ip, server_port):
    server = ThreadedTCPServer((server_ip, server_port), MyTCPHandler)
    ip, port = server.server_address
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    print("Server loop running in thread:", server_thread.name)
    print("IP: {}, PORT: {}".format(ip, port))
    server.rcv_msg = None
    return server


def stop_server(server):
    server.shutdown()
    server.server_close()
