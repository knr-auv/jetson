import threading

from controlThread.controlThread import controlThread
from cameraStream.stream import cameraStream
class autonomy(threading.Thread):
    def __init__(self,controlThread = controlThread(), stream = cameraStream()):
        threading.Thread.__init__(self)
        self.active = False

    def run(self):
        self.active = True
        while self.active:
            pass
