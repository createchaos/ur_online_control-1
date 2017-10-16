'''
Created on 15.10.2017

@author: rustr
'''

def flatten_list(array, return_array = []):  
    if type(array) == list or type(array) == tuple:
        for x in array:
            return_array += flatten_list(x, [])
    else:
        return_array += [array]
    return return_array

 
def divide_list_by_number(array, number):
    if len(array) % number != 0:
        raise Exception("len(array) % number != 0")
    return [array[x:x+number] for x in range(0, len(array), number)]
