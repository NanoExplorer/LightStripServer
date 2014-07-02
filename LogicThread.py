from threading import *
import time

class WorkerThread(Thread):
    """Thread that launches the convert() method to make the network server responsive"""
    def __init__(self, message):
        """Initialize thread"""
        Thread.__init__(self)
        self.message = message
        self.start()
        
    def run(self):
        time.sleep(1) #simulate long running ness
        print self.message
        
