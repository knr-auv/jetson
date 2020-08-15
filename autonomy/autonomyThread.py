import threading, time

from controlThread.controlThread import controlThread
from cameraStream.stream import cameraStream
class autonomy(threading.Thread):
    def __init__(self,controlThread = controlThread(), stream = cameraStream()):
        threading.Thread.__init__(self)
        self.active = False
        print("autonomy")

    def run(self):
        self.active = True
        while self.active:
            time.sleep(1)
            print("running")
            pass
