"""Module similar to logging. It is thread safe and allows to log data from anywhere in the code"""

import time
import math
from threading import Lock

__logger_lock = Lock()
__start_time = time.time()
__streamWrite = print
__streamClose = None

def setStream(stream, streamClose):
    global __streamWrite
    __streamWrite= stream
    global __streamClose
    __streamClose= streamClose

def write(msg, caller):
    """ For example: Logger.write('hello','autonomyThread') """
    current_time = (time.time()-__start_time)
    hours= math.floor(current_time/3600)
    current_time-=hours*3600
    minutes = math.floor(current_time/60)
    current_time-=minutes*60
    seconds=math.floor(current_time)
    current_time-=seconds
    current_time=math.floor(current_time*10)
    time_str = "%02d:%02d:%02d.%1d" % (hours,minutes,seconds,current_time)
    with __logger_lock:
        __streamWrite(time_str+' '+str(caller)+': '+msg)
