import threading

class cameraStream(threading.Thread):
    active = True
    def __init__(self):

        pass
    def stop(self):
        self.active = False
    def run(self):
        pass
    def getFrame(self):
        
        pass