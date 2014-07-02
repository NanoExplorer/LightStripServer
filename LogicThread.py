from threading import *
import time
import random

class WorkerThread(Thread):
    """Thread that launches the convert() method to make the network server responsive"""
    def __init__(self):
        """Initialize thread"""
        Thread.__init__(self)
        self.message = ""
        self.cond = Condition()
        self.start()
        
    def run(self):
        while True:
            print "waiting..."
            with(self.cond):
                self.cond.wait()
                print self.message

    def message(self, data):
        with(self.cond):
            self.message = data
            self.cond.notifyAll()
        
    
