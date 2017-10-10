'''
Created on 13.02.2015

@author: rustr
'''


def clamp(value, minv, maxv):
    value = min([value, maxv])
    value = max([value, minv])
    return value

def map_range(value,fromMin,fromMax,toMin,toMax):
    fromSpan = fromMax - fromMin
    toSpan = toMax - toMin
    valueScaled = float(value-fromMin)/float(fromSpan)
    return toMin + (valueScaled * toSpan)