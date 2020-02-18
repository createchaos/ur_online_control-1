from __future__ import absolute_import

from ...communication.tcp_server import TCPFeedbackServer, FeedbackHandler

def isclose(a, b, rel_tol=1e-09, abs_tol=0.0):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class ServerMixins:
    def add_message(self, message):
        i = len(self.received_messages)
        message = message.decode('utf-8')
        if message == 'Done':
            self.received_messages[i] = message
        else:
            msg = message.split('[', 1)[1].split(']')[0]
            msg = msg.split(',')
            msg = [float(crd)*1000 if c not in [3, 4, 5] else float(crd) for c, crd in enumerate(msg)]
            self.received_messages[i] = msg

    def check_exit(self, tol=50):
        if "Done" in self.received_messages.values():
            return True
        elif len(self.received_messages) == self.checked_messages:
            return False
        else:
            msg = self.received_messages[self.checked_messages]
            self.checked_messages += 1
            if type(msg) == list and type(self.exit_message) == list:
                return all(isclose(msg[i], self.exit_message[i], abs_tol=tol) for i in range(len(msg)))
            elif msg == self.exit_message or msg == 'Done':
                return True

    def get_server(self, server):
        if server is None:
            self.start_server()
            self.server_running = True
            self.server_started = True
        else:
            self.server_thread = server
        self.server = self.server_thread.get()
        self.server.rcv_msg = []

    def start_server(self):
        self.server_thread = TCPFeedbackServer(self.server_ip, self.server_port, FeedbackHandler)
        self.server_thread.start()
        print("Server loop running in thread:", self.server_thread.t.name)
        print("IP: {}, PORT: {}".format(self.server_thread.ip, self.server_thread.port))

    def server_listen(self):
        while not self.check_exit():
            #print(self.server.rcv_msg)
            self.server = self.server_thread.get()
            if self.server.rcv_msg is None:
                pass
            elif type(self.server.rcv_msg) != list and len(self.received_messages) < 1:
                self.add_message(self.server.rcv_msg)
            elif type(self.server.rcv_msg) == list and len(self.received_messages) < len(self.server.rcv_msg):
                if len(self.received_messages) is None:
                    ind = 0
                else:
                    ind = len(self.received_messages)
                self.add_message(self.server.rcv_msg[ind][0])
                print(self.server.rcv_msg)
            else:
                pass
        else:
            if self.server_started:
                self.stop_server()
            else:
                pass

    def stop_server(self):
        self.server_thread.close()
        self.server_thread.join()

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
