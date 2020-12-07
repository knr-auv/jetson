import time, math
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
    t = (time.time()-__start_time)
    h = m = math.floor(t/3600)
    t-=h*3600
    m = math.floor(t/60)
    t-=m*60
    s=math.floor(t)
    t-=s
    t=math.floor(t*10)
    t = "%02d:%02d:%02d.%1d" % ( h,m, s, t) 
    with __logger_lock:
        __streamWrite(t+' '+str(caller)+': '+msg)
