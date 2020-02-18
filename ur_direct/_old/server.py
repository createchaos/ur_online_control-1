from __future__ import absolute_import

import sys
if sys.version_info[0] == 2:
    from SocketServer import TCPServer, ThreadingMixIn, StreamRequestHandler
elif sys.version_info[0] == 3:
    from socketserver import TCPServer, ThreadingMixIn, StreamRequestHandler

__all__ = [
    'MyTCPHandler',
    'ThreadedTCPServer'
]


# class MyTCPHandler(BaseRequestHandler):
#     def handle(self):
#         # self.request is the TCP socket connected to the client
#         data = self.request.recv(1024)
#         data = data.decode('utf-8')
#         data = data.split('\n')
#         self.server.rcv_msg = data


class MyTCPHandler(StreamRequestHandler):
    def handle(self):
        data = self.rfile.readlines()
        data = [line.strip() for line in data]
        self.server.rcv_msg.append(data)


class ThreadedTCPServer(ThreadingMixIn, TCPServer):
    timeout = 1
