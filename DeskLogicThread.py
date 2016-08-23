from threading import *
import time
import random
class ImageManager:
    def __init__(self):
        self.gamma = bytearray(256)
        for i in range(256):
            self.gamma[i] = 0x80 | int(pow(float(i)/255.0, 2.5) * 127.0 + 0.5)

        self.STRIPLEN = 32 # configurable to however many pixels you have on your led strip
        self.COLORLEN = self.STRIPLEN * 3 #Colorlen is the size of the part of the array containing actual
                                          #color information.
        self.ARRAYLEN = self.COLORLEN + 1 #Arraylen is the size of the whole array.
        self.lights = bytearray([0x80 for x in range(self.ARRAYLEN)])
        self.lights[self.ARRAYLEN - 1] = 0

        self.DEV = '/dev/spidev0.1'
        self.spidev = open(self.DEV, 'wb')
        
    def write(self, red,green,blue):
        for x in range(self.STRIPLEN):
            self.setpixel((red,green,blue), x)
        self.output()
        
    def setpixel(self, pixel, position):
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
            self.setpixel((0,0,0), x)
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
        self.lights = ImageManager()
        self.start()
        
        
    def run(self):
        while self.keepGoing:
            if self.message != "":
                self.processMessage()
            #print("waiting...")
            
            with(self.cond):
                self.cond.wait()
                
    """
    Posts a message and tells the run method to process it.

    The message will be in the format 'qualifier : data'
    For now, the only qualifier is ALT, meaning altitude. (above body's surface or MSL)
    """
    def sendMessage(self, data):
        with(self.cond):
            self.message = data.decode('utf-8').strip()
            self.cond.notifyAll()

    def stop(self):
        with(self.cond):
            self.keepGoing = False
            self.cond.notifyAll()
            self.lights.blackout()

    def processMessage(self):
        try:
            info = self.message.split(':')
            red=int(info[0])
            green=int(info[1])
            blue=int(info[2])
            if red>=0 and red<=255 and blue>=0 and blue<=255 and green>=0 and green<=255:
                self.lights.write(red,green,blue)
        except:
            pass
        
