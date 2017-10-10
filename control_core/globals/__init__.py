""" 
SANS 0.2
Created on Nov 2, 2012
@author: Kathrin & Romana
"""

from data_queues import DataQueue, DataQueues, DataLifoQueue
from client_objects_container import ClientObjectsContainer
from message_identifiers import *
from client_states import *

#===============================================================================
" A container for all DataQueues from the various clients "
RECEIVE_QUEUES = DataQueues()
SEND_QUEUES = DataQueues()
INTERRUPT_QUEUES = DataQueues()
#===============================================================================
" A container for all Client Objects for various clients "
" Client Objects can be Actuators (UR, ABB, etc.) or Sensors"
CLIENT_OBJECTS = ClientObjectsContainer()
#===============================================================================

SMALL_VALUE = 0.00000001

SAVE_DATA = False
STOP_AT_NO_CURRENT = False

