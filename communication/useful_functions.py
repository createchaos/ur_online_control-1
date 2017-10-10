'''
Created on 11.12.2014

@author: rustr
'''

import sys, os
import pkgutil

def reload_modules_of_folder(folder, exceptions=[]):
    
    folder_and_sub_folders = [x[0] for x in os.walk(folder) if  os.path.basename(x[0])[0] != "."]

    for f in folder_and_sub_folders:
        M = [name for _, name, _ in pkgutil.iter_modules([f])]
        for m in M:
            if sys.modules.has_key(m) and m not in exceptions:
                print "Module %s is being reloaded." % m
                sys.modules.pop(m)


def flatten_tree(tree):
    alist = []
    for i in range(tree.BranchCount):
        branchList = tree.Branch(i)
        for item in branchList:
            if item != None:
                alist.append(item)
    return alist

def tree_to_list(tree):
    alist = []
    for i in range(tree.BranchCount):
        alist.append(list(tree.Branch(i)))
    return alist

def map_range(value,fromMin,fromMax,toMin,toMax):
    fromSpan = fromMax - fromMin
    toSpan = toMax - toMin
    valueScaled = float(value-fromMin)/float(fromSpan)
    return toMin + (valueScaled * toSpan)

def clamp(value, minv, maxv):
    value = min([value, maxv])
    value = max([value, minv])
    return value

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

def divide_list(alist, number):
    if len(alist) % number != 0:
        raise Exception("len(alist) % number != 0")
    else:
        new_list = []
        for x in range(0, len(alist), number):
            new_list.append(alist[x:x+number])
        return new_list



def list_to_tree(input, none_and_holes=False, base_path=[0]):
    """
    Transforms nestings of lists or tuples to a Grasshopper DataTree
    Usage:
    mytree = [ [1,2], 3, [],[ 4,[5]] ]
    a = list_to_tree(mytree)
    b = list_to_tree(mytree, none_and_holes=True, base_path=[7,1])
    """

    from Grasshopper import DataTree as Tree
    from Grasshopper.Kernel.Data import GH_Path as Path
    from System import Array
    
    def process_one_item(input,tree,track):
        path = Path(Array[int](track))
        if len(input) == 0 and none_and_holes: tree.EnsurePath(path); return
        for i,item in enumerate(input):
            if hasattr(item, '__iter__'): #if list or tuple
                track.append(i); process_one_item(item,tree,track); track.pop()
            else:
                if none_and_holes: tree.Insert(item,path,i)
                elif item is not None: tree.Add(item,path)
    tree = Tree[object]()
    if input is not None: process_one_item(input,tree,base_path[:]); return tree


def linear_interpolation(x, x_values, y_values, constrain=True):
    """ we have a function f(x) = y defined by x_values and y_values.
    Now we want to find the y value for a other x value or another x list.
    """
    import numpy as np

    idx_min = np.argmin(x_values)
    idx_max = np.argmax(x_values)

    xmin, xmax = x_values[idx_min], x_values[idx_max]
    
    def interpolate_one(x):
    
        if x == xmin:
            return y_values[idx_min]
        if x == xmax:
            return y_values[idx_max]
    
        if constrain:
            if x < xmin: return y_values[idx_min]
            if x > xmax: return y_values[idx_max]
        else:
            if x < xmin or x > xmax:
                raise Exception("x value is out of bounds")
            
        idx1, idx2 = np.argsort(np.fabs(x_values - x))[:2]
        return map_range(x, x_values[idx1], x_values[idx2], y_values[idx1], y_values[idx2])
    
    interpolate_multiple = np.vectorize(interpolate_one)
    
    return interpolate_multiple(x)

    
    
    
if __name__ == "__main__":
    alist = range(9)
    print divide_list(alist, 3)

