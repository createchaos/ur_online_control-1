'''
Created on 09.10.2017

@author: rustr
'''

import os

HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, '../../'))
DATA = os.path.abspath(os.path.join(HOME, 'data'))
DOCS = os.path.abspath(os.path.join(HOME, 'docs'))
TEMP = os.path.abspath(os.path.join(HOME, 'temp'))


def get(filename):
    filename = filename.strip('/')
    return os.path.abspath(os.path.join(DATA, filename))


__all__ = []