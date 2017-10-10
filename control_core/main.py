'''
Created on 22.11.2016

@author: rustr
'''

from operation import OperationThread, Operation

from server import Server

import globals
import socket


def main():
            
    # start the server
    server = Server()
    server.start()
    
    # start the fabrication process with name of the function and necessary clients
    operation = Operation("SWC_Operation_160228", ["UR5", "GH"])
      
    server.quit()
    server.join()
     
if __name__ == "__main__":
    main()  
    
    
    