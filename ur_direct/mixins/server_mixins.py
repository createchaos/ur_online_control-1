from __future__ import absolute_import

import math
import threading
from ..server import ThreadedTCPServer, MyTCPHandler


class ServerMixins:
    def add_message(self, message):
        i = len(self.received_messages)
        if message == 'Done':
            self.received_messages[i] = message
        else:
            msg = message.split('[', 1)[1].split(']')[0]
            msg = msg.split(',')
            msg = [float(crd)*1000 if c not in [3, 4, 5] else float(crd) for c, crd in enumerate(msg)]
            self.received_messages[i] = msg

    def check_exit(self, tol=100):
        if "Done" in self.received_messages.values():
            return True
        elif len(self.received_messages) == self.checked_messages:
            return False
        else:
            msg = self.received_messages[self.checked_messages]
            self.checked_messages += 1
            if type(msg) == list and type(self.exit_message) == list:
                return all(math.isclose(msg[i], self.exit_message[i], abs_tol=tol) for i in range(len(msg)))
            elif msg == self.exit_message or msg == 'Done':
                return True

    def start_server(self):
        server = ThreadedTCPServer((self.server_ip, self.server_port), MyTCPHandler)
        ip, port = server.server_address
        server.rcv_msg = None
        self.server_thread = threading.Thread(target=server.serve_forever)
        self.listen_thread = threading.Thread(target=self.server_listen, args=(server,))
        self.server_thread.daemon = False
        self.listen_thread.daemon = True
        self.server_thread.start()
        self.listen_thread.start()
        print("Server loop running in thread:", self.server_thread.name)
        print("IP: {}, PORT: {}".format(ip, port))

    def server_listen(self, server):
        i = 0
        while not self.check_exit():
            print(server.rcv_msg, i)
            if server.rcv_msg is None:
                server.handle_request()
                i += 1
                if i == 100:
                    self.stop_server(server)
                    break
            elif type(server.rcv_msg) != list and len(self.received_messages) < 1:
                self.add_message(server.rcv_msg)
                break
            elif type(server.rcv_msg) == list and len(self.received_messages) < len(server.rcv_msg):
                ind = len(self.received_messages)
                self.add_message(server.rcv_msg[ind])
                break
            else:
                self.received_messages[0] = server.rcv_msg
                self.stop_server(server)
                break

    def stop_server(self, server):
        server.shutdown()
        server.server_close()

# if __name__ == "__main__":
#     messages = ['p[1.6,2.8,6.4,0,0,0]', 'Done']
#     received_messages = {}
#     for i, message in enumerate(messages):
#         if message == 'Done':
#             received_messages[i] = message
#         else:
#             msg = message.split('[', 1)[1].split(']')[0]
#             msg = msg.split(',')
#             msg = [float(crd)*1000 if c not in [3, 4, 5] else float(crd) for c, crd in enumerate(msg)]
#             received_messages[i] = msg
#     print(received_messages)
#
#     def check_exit(received_messages, exit_message=[1600., 2800., 6400., 0., 0., 0.], tol = 100):
#         global checked_messages
#         if len(received_messages) == checked_messages:
#             return False
#         else:
#             msg = received_messages[checked_messages]
#             print(msg)
#             checked_messages += 1
#             if type(msg) == list and type(exit_message) == list:
#                 return all(math.isclose(msg[i], exit_message[i], abs_tol=tol) for i in range(len(msg)))
#             elif msg == exit_message or msg == 'Done':
#                 return True
#
#     checked_messages = 0
#     while not check_exit(received_messages):
#         print(received_messages)
