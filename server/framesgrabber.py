import threading

class FramesGrabber(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        while True:
            pass
           # ret = self.cap.grab()
    
    def getFrame(self):
        return cap.retrieve()
    
