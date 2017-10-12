'''
Created on 12.10.2017

@author: rustr
'''


def divide_list(array, number):
    """Create sub-lists of the list defined by number. 
    """
    if len(array) % number != 0:
        raise Exception("len(alist) % number != 0")
    else:
        return [array[x:x+number] for x in range(0, len(array), number)]

def format_commands(msg_float_list):
    return commands