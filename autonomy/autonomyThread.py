import threading

from controlThread.controlThread import controlThread
class autonomy(threading.Thread):
    def __init__(self,controlThread = controlThread()):
        threading.Thread.__init__(self)
        self.active = False

    def run(self):
        self.active = True
        while self.active:
            pass
