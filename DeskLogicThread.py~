from threading import *
import time
import random
class ImageManager:
    def __init__(self):
        self.gamma = bytearray(256)
        for i in range(256):
            self.gamma[i] = 0x80 | int(pow(float(i)/255.0, 2.5) * 127.0 + 0.5)
        self.SKY = (0, 30, 50)
        self.GROUND = (0, 100, 0)
        self.SHIP = (100, 100, 0)
        self.STRIPLEN = 32 # configurable to however many pixels you have on your led strip
        self.COLORLEN = self.STRIPLEN * 3 #Colorlen is the size of the part of the array containing actual
                                          #color information.
        self.ARRAYLEN = self.COLORLEN + 1 #Arraylen is the size of the whole array.
        self.lights = bytearray([0x80 for x in range(self.ARRAYLEN)])
        self.lights[self.ARRAYLEN - 1] = 0

        self.DEV = '/dev/spidev0.0'
        self.spidev = file(self.DEV, 'wb')
        
    def write(self, position, scale):
        for x in range(self.STRIPLEN):
            self.set(self.SKY, x)
        self.set(self.GROUND, 0)

        shipPos = int(position/float(scale) * 30 + 1)
        self.set(self.SHIP, shipPos)
        self.output()
        
    def set(self, pixel, position):
        """
        Sets a certain pixel of the strip (at 'position') to the color tuple 'pixel'
        """
        index = position * 3
        red, green, blue = pixel
        self.lights[index] = self.gamma[green]
        self.lights[index + 1] = self.gamma[red]
        self.lights[index + 2] = self.gamma[blue]
    
    def blackout(self):
        for x in range(self.STRIPLEN):
            self.set((0,0,0), x)
        self.output()

    def output(self):
        """
        Actually writes the array to the physical strip
        """
        self.spidev.write(self.lights)
        self.spidev.flush()

class WorkerThread(Thread):
    """Aims to make the network server very responsive"""
    def __init__(self):
        """Initialize thread"""
        Thread.__init__(self)
        self.message = ""
        self.cond = Condition()
        self.keepGoing = True
        self.scaleTop = 0
        self.lights = ImageManager()
        self.start()
        
        
    def run(self):
        while self.keepGoing:
            if self.message != "":
                self.processMessage()
            #print "waiting..."
            
            with(self.cond):
                self.cond.wait()
                
    """
    Posts a message and tells the run method to process it.

    The message will be in the format 'qualifier : data'
    For now, the only qualifier is ALT, meaning altitude. (above body's surface or MSL)
    """
    def sendMessage(self, data):
        with(self.cond):
            self.message = data
            self.cond.notifyAll()

    def stop(self):
        with(self.cond):
            self.keepGoing = False
            self.cond.notifyAll()
            self.lights.blackout()

    def processMessage(self):
        data = ""
        with(self.cond): #I'm not quite sure I'm doing this lock thing right.
            info = self.message.split(':')

            if info[0] == 'ALT':
                #process altitude information
                altitude = float(info[1])
                self.getNewScale(self.scaleTop, altitude)
                self.lights.write(altitude, self.scaleTop)

    def getNewScale(self, currentTop, currentPos):
        """ONLY call this method from inside processMessage"""
        if currentTop == 0:
            self.changeScale(currentPos * 2)
        elif currentTop < currentPos:
            self.changeScale(currentPos * 30)
        elif currentTop > currentPos * 30:
            self.changeScale(currentPos)
    
    def changeScale(self, newScale):
        """ONLY call this method from inside getNewScale"""
        if newScale > 32:
            self.scaleTop = newScale
        else:
            self.scaleTop = 32
        print self.scaleTop
#TODO: add speaking scale changer dude.
