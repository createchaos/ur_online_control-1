'''

Created on 08.11.2013

@author: rustr
'''

import time
from threading import Lock
import copy

from Queue import Queue, LifoQueue

class DataQueues():
    """ A container for all DataQueues from the clients.
    
    Usage: 
    in ClientSocket __init__, e.g. self.identifier = client_id, message identifier = MSG_STRING
    Global.DATA_QUEUES.append(DataQueue(self.identifier, MSG_STRING))
    in order to get or put something from this queue:
    dQ = Global.DATA_QUEUES.get(self.identifier, MSG_STRING)
    dQ.put(data) / data = dQ.get() => have a look into DataQueue for options
    """
    
    def __init__(self):
        self.queues = {}
        "{'Rhino': {MSG_STRING: DataQueue, MSG_FLOAT: DataQueue}, 'UR': {MSG_COMMAND: DataQueue}}"
        #self.lock = Lock()
        self.lock = Lock()
        
    def append(self, dataqueue, *args):
        
        self.lock.acquire()
        
        if len(args) == 2:
            "Option 1: append with identifier, with msg_id: used for receive queues."
            identifier = [i for i in args if type(i) == type(str())][0]
            msg_id = [i for i in args if type(i) == type(int())][0]
            if not identifier in self.queues:
                self.queues.update({identifier:{}})
            
            self.queues[identifier].update({msg_id:dataqueue})
        
        elif len(args) == 1:
            
            if type(args[0]) == type(str()):
                "Option 2: append with identifier, without msg_id: used for send queues."
                identifier = args[0]
                self.queues.update({identifier:dataqueue})
            
            elif type(args[0]) == type(int()):
                "Option 3: append with just msg_id: used for receive queues in Clients."
                msg_id = args[0]
                self.queues.update({msg_id:dataqueue})
            else:
                raise Exception("DataQueues: No arguments given.")
            
        else: # 'identifier' not in params and 'msg_id' in params
            raise Exception("DataQueues: No arguments given.")
        
        self.lock.release()
    
    def get(self, *args):
        
        self.lock.acquire()
        
        if len(args) == 2:
            identifier = [i for i in args if type(i) == type(str())][0]
            msg_id = [i for i in args if type(i) == type(int())][0]
            self.lock.release()
            return self.queues[identifier][msg_id]
        
        elif len(args) == 1:
            self.lock.release()
            return self.queues[args[0]]
            
            
        else:
            self.lock.release()
            raise Exception("DataQueues: No args given.")
    
    def release(self):
        self.lock.release()


class DataLifoQueue(object):
    
    def __init__(self):
        self.maxsize = 100000
        self.queue = LifoQueue()
        
    def clear(self):
        del(self.queue.queue[:])
    
    def length(self):
        return self.queue.qsize()
    
    def put(self, data, time_stamp = None, wait = True, timeout = 0):
        
        if not time_stamp:
            time_stamp = time.time()
                                
        if self.queue.empty(): # The queue is empty, put item on queue
            self.queue.put([data, time_stamp])
        elif self.length() < self.maxsize: # The queue is not empty, but is not yet full, put item on queue
            self.queue.put([data, time_stamp])
        else: # len(self.queue) == self.maxsize
            self.queue.get() # throw something off
            self.queue.put([data, time_stamp])
        return True
    
    def full(self):
        return self.queue.full()
    
    def empty(self):
        return self.queue.empty()
    
    def get_all(self, **params):
        time_stamp = params['time_stamp'] if 'time_stamp' in params else False
        all_data_ts = self.queue.queue[:] # thread safe ?
        all_data = [data for data, ts in all_data_ts] 
        all_ts =  [ts for data, ts in all_data_ts] 
        if time_stamp:
            return all_data, all_ts
        else:
            return all_data
    
    def get_last(self):
        #return copy.deepcopy(self.queue.queue[-1])
        return self.get()
    
    def get_average(self, num):
        values_sum = 0
        for i in range(num):
            print self.get()
            values_sum += self.get()[0]
        return values_sum/num
    
    def get(self, **params):
        """ 
        Options:
        
        1. no options: get an item off the queue, if its empty return None
        2. If wait: wait until there is an item on the queue, return item
        3. If get_all: get all items off the queue, return list
        4. If keep_data: in any options: don't delete the item or items
        """
        
        time_stamp = params['time_stamp'] if 'time_stamp' in params else False
        blk = params['block'] if 'block' in params else False
        to = params['timeout'] if 'timeout' in params else None
        
        data, ts = self.queue.get(block=blk, timeout=to)

        if time_stamp:
            return data, ts  
        else:  
            return data
    

class DataQueue(object):
    
    def __init__(self, **params):
        self.maxsize = 100000
        self.queue = Queue(100000)
        self.single_item = params['single_item'] if 'single_item' in params else False
    
    def set_single_item(self, b):
        self.single_item = b
    
    def length(self):
        return self.queue.qsize()
    
    def put(self, data, time_stamp = None, wait = True, timeout = 0):
        
        if not time_stamp:
            time_stamp = time.time()
                                
        if self.queue.empty(): # The queue is empty, put item on queue
            self.queue.put([data, time_stamp])
            
        elif self.length() < self.maxsize: # The queue is not empty, but is not yet full, put item on queue
            
            if self.single_item == False:
                self.queue.put([data, time_stamp])
            else:
                self.queue.get()
                self.queue.put([data, time_stamp])
            
        else: # len(self.queue) == self.maxsize
            if wait == True:
                self.queue.put([data, time_stamp])
            else:
                return False
        return True
    
    def full(self):
        return self.queue.full()
    
    def empty(self):
        return self.queue.empty()
    
    def clear(self):
        self.queue.queue.clear()
        
    def get(self, **params):
        """ 
        Options:
        
        1. no options: get an item off the queue, if its empty return None
        2. If wait: wait until there is an item on the queue, return item
        3. If get_all: get all items off the queue, return list
        4. If keep_data: in any options: don't delete the item or items
        """
        
        get_all = params['get_all'] if 'get_all' in params else False
        keep_data = params['keep_data'] if 'keep_data' in params else False
        time_stamp = params['time_stamp'] if 'time_stamp' in params else False
        timeout = params['timeout'] if 'timeout' in params else 0
        
        data = []
        ts = []
        
        if not self.empty():
            if get_all:
                while not self.empty():
                    d, t = self.queue.get()
                    data.append(d)
                    ts.append(t)
                if keep_data:
                    data_cp = copy.deepcopy(data)
                    ts_cp = copy.deepcopy(ts)
                    for d, t in zip(data_cp, ts_cp):
                        self.queue.put([d, t])
            else:
                data, ts = self.queue.get()
                if keep_data:
                    self.queue.put([data, ts])
        
        if time_stamp:
            return data, ts  
        else:  
            return data
        
        
        

#===============================================================================

if __name__ == "__main__":
    
    
    
    q = DataLifoQueue()
    for i in range(10):
        q.put(i)
    
    print q.get_last()
    q.clear()
    print q.get_all()
    for i in range(10):
        q.put(i)
    print q.get_all()
        
    
    