'''
S.A.N.S V0.1

Created on Nov 7, 2012
@author: Kathrin & Romana
'''

import globals
import time
import numpy as np


def wait_for_client(client_id, state):
    #print "OPERATION_THREAD: waiting for client %s to enter state %s." % (client_id, globals.client_states_str_array[state])
    client_object = globals.CLIENT_OBJECTS.get(client_id)
    while client_object.state != state:
        time.sleep(0.00001)
    #print "OPERATION_THREAD: stop waiting for client %s to enter state %s." % (client_id, globals.client_states_str_array[state])


def wait_for_client_message(client_id, msg_id):
    dQ = globals.RECEIVE_QUEUES.get(client_id, msg_id)
    while dQ.empty():
        time.sleep(0.00001)
    msg = dQ.get(wait=True)
    return msg

def flatten_list(alist):
    flattened_list = []
    
    def recall(l, list_to_append):
        if type(l) == list or type(l) == tuple:
            for x in l:
                list_to_append += recall(x, [])
        else:
            # item
            list_to_append += [l]
        return list_to_append
    
    return recall(alist, flattened_list)

def divide_float_list(l, num):
    counter = 0
    new_list = []
    if len(l) % num != 0:
        print "Can not divide list"
    for i in range(len(l)/num):
        new_list.append(l[counter:(counter+num)])
        counter+=num
    return new_list

if __name__ == "__main__":
    
    a = (1, (2,3))
    b = (4, 5)
    c = ([6,7,8], 9)
    d = ([[10,11],[12,13]], 14)
    
    e = [a, b, c, d]
    print flatten_list(e)
    
    """
    print e
    x = [item for sublist in e for item in sublist]
    print x
    x = [item for sublist in x for item in sublist]
    print x
    """
    
    
    """
    b = [-33.23720169067383, -17.60194969177246, 7.899301052093506, -33.365570068359375, -13.652798652648926, 7.899301052093506, -32.658203125, -10.57268238067627, 7.899301052093506, -31.382579803466797, -8.169318199157715, 7.899301052093506, -29.806177139282227, -6.250421524047852, 7.899301052093506, -28.196474075317383, -4.623710632324219, 7.899301052093506, -26.82094955444336, -3.0969009399414062, 7.899301052093506, -25.929893493652344, -1.48379647731781, 7.899301052093506, -25.378286361694336, 0.2617937922477722, 7.899301052093506, -24.625802993774414, 2.046055555343628, 7.899301052093506, -23.114927291870117, 3.769087553024292, 7.899301052093506, -20.288145065307617, 5.330987930297852, 7.899301052093506, -15.587942123413086, 6.631855487823486, 7.899301052093506, -8.456803321838379, 7.571788787841797, 7.899301052093506]

    
    a = float_array_3D_to_V3(b)

    print a
    
    #a_mirror = mirror_yz(a)
    #print a_mirror
    
    b = flatten_V3_array(a)
    print b
    
    a = float_array_3D_to_V3(b)
    print a
    """
    
