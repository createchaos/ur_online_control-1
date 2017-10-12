'''
Created on 27.09.2016

@author: rustr
'''

from ur_online_control.control_core.server.base_client import BaseClient

class GHClient(BaseClient):
    
    def __init__(self, host = '127.0.0.1', port = 30003): 
        super(GHClient, self).__init__("GH", host, port)
    
    def stdout(self, msg):
        #from Rhino.RhinoApp import WriteLine
        #WriteLine("%s: %s" % (self.identifier, str(msg)))
        print msg
        
        
if __name__ == "__main__":
    server_address = "192.168.10.12"
    server_port = 30003
    client = GHClient(server_address, server_port)
    client.connect_to_server()    
    client.start()
    
    
