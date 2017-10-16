from threading import Thread, Timer, Condition
import time
import random
import traceback
import animations
class ImageManager:
    def __init__(self):
        self.gamma = bytearray(256)
        for i in range(256):
            self.gamma[i] = 0x80 | int(pow(float(i)/255.0, 2.5) * 127.0 + 0.5)

        self.STRIPLEN = 32+ 24 # configurable to however many pixels you have on your led strip
        self.COLORLEN = self.STRIPLEN * 3 #Colorlen is the size of the part of the array containing actual
                                          #color information.
        self.ARRAYLEN = self.COLORLEN + 2 #Arraylen is the size of the whole array.
        self.lights = bytearray([0x80 for x in range(self.ARRAYLEN)])
        self.lights[0] = 0
        self.lights[self.ARRAYLEN-1] = 0
        self.DEV = '/dev/spidev1.0'
        self.spidev = open(self.DEV, 'wb')
        self.allow_anim = 0
        self.allow_timer = True
        self.periodicRefresh(600)

    def write(self, red,green,blue):
        self.allow_anim = 0
        for x in range(self.STRIPLEN):
            if x < 0:
                self.setpixel((0,0,0),x)
            else:
                """if red != 0:
                    red2 = red - 1 + x%3
                if red != 0:
                    blue2 = red - 1 + (x+1)%3
                    print("Changed blue from {} to {}".format(blue,blue2))
                if green != 0:
                    green2 = green - 1 + (x+2)%3
                """
                self.setpixel((red,green,blue), x)
        self.output()
        
    def setpixel(self, pixel, position):
        """
        Sets a certain pixel of the strip (at 'position') to the color tuple 'pixel'
        """
        index = position * 3
        red, green, blue = pixel
        #self.lights[index + 1] = 0x80 | (green//2)#self.gamma[green]
        #self.lights[index + 2] = 0x80 | (red//2)#self.gamma[red]
        #self.lights[index + 3] = 0x80 | (blue//2)#self.gamma[blue]

        self.lights[index + 1] = self.gamma[green]
        self.lights[index + 2] = self.gamma[red]
        self.lights[index + 3] = self.gamma[blue]
    def setrawpixel(self,pixel,position):
        index = position * 3
        red, green, blue = pixel
        self.lights[index + 1] = 0x80 | (green//2)#self.gamma[green]
        self.lights[index + 2] = 0x80 | (red//2)#self.gamma[red]
        self.lights[index + 3] = 0x80 | (blue//2)#self.gamma[blue]
        
    def stop(self):
        try:
            self.timer.cancel()
            self.anim.cancel()
            self.allow_anim = 0
            self.allow_timer = False
        except:
            time.sleep(1)
        for x in range(self.STRIPLEN):
            self.setpixel((0,0,0), x)
        self.output()
    def animate(self, animationName):
        self.animation = animations.getAnimator(animationName,self.STRIPLEN)
        self.allow_anim += 1
        self.animupdate(self.allow_anim)
    def animupdate(self,anim_ID):
        if self.allow_anim == anim_ID:
            self.animation.update()
            l = self.animation.getLights()
            if self.animation.needsRaw():
                for i,rgb in enumerate(l):
                    self.setrawpixel(rgb,i)
            else:
                for i,rgb in enumerate(l):
                    self.setpixel(rgb,i)
            self.output()
            self.anim = Timer(0.03,self.animupdate,args=[anim_ID])
            self.anim.start()

    def output(self):
        """
        Actually writes the array to the physical strip
        """
        self.spidev.write(self.lights)
        #print("Wrote {} to file".format(self.lights))
        self.spidev.flush()
    def periodicRefresh(self,interval):
        if self.allow_timer:
            self.timer = Timer(interval,self.periodicRefresh,args=[interval])
            #print("AUTO REFRESH")
            self.output()
            self.timer.start()

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
    """
    def sendMessage(self, data):
        with(self.cond):
            self.message = data.decode('utf-8').strip()
            self.cond.notifyAll()

    def stop(self):
        with(self.cond):
            self.keepGoing = False
            self.cond.notifyAll()
            self.lights.stop()


    def processMessage(self):
        if self.message.split('.')[0] == 'anim':
            try:
                self.lights.animate(self.message.split('.')[1])
            except:
                print(traceback.format_exc())
        else:
            try:
                info = self.message.split(':')
                red=int(info[0])
                green=int(info[1])
                blue=int(info[2])
                if red>=0 and red<=255 and blue>=0 and blue<=255 and green>=0 and green<=255:
                    self.lights.write(red,green,blue)
            except:
                pass
        
