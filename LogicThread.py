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
        self.keepGoing = True
        self.start()
        
    def run(self):
        while self.keepGoing:
            if self.message != "":
                print self.message
            print "waiting..."
            
            with(self.cond):
                self.cond.wait()
                

    def sendMessage(self, data):
        with(self.cond):
            self.message = data
            self.cond.notifyAll()

    def stop():
        self.keepGoing = False
        with(self.cond):
            self.cond.notifyAll()
    
