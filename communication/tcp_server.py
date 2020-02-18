from __future__ import absolute_import

import sys
import threading
if sys.version_info[0] == 2:
    import SocketServer as ss
elif sys.version_info[0] == 3:
    import socketserver as ss
ss.TCPServer.allow_reuse_address = True

__all__ = [
    'FeedbackHandler',
    'TCPFeedbackServer'
]


class FeedbackHandler(ss.StreamRequestHandler):
    def handle(self):
        data = self.rfile.readlines()
        data = [line.strip() for line in data]
        self.server.rcv_msg.append(data)


class ThreadedTCPServer(ss.ThreadingMixIn, ss.TCPServer):
    allow_reuse_address = True
    timeout = 1


class TCPFeedbackServer:
    def __init__(self, ip="192.168.10.11", port=50002, handler=FeedbackHandler):
        self.ip = ip
        self.port = port
        self.handler = handler

        self.reset()

    def reset(self):
        self.server = ThreadedTCPServer((self.ip, self.port), self.handler)
        self.server.rcv_msg = []
        self.t = threading.Thread(target=self.server.serve_forever)
        self.t.daemon = True

    def get(self):
        return self.server

    def start(self):
        self.t.start()
        print("Server running...")

    def close(self):
        self.server.shutdown()
        self.server.server_close()

    def join(self):
        self.t.join()

    def is_alive(self):
        return self.t.is_alive()
