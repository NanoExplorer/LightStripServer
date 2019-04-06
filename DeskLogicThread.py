from threading import Thread, Timer, Condition
import time
import random
import traceback
import animations
class ImageManager:
    def __init__(self):
        self.gamma = bytearray(256)
        for i in range(256):
            if i>0 and i<28:
                self.gamma[i] = 0x81
            else:
                self.gamma[i] = 0x80 | int(pow(float(i)/255.0, 2.5) * 127.0 + 0.5)

        self.STRIPLEN = 32+ 23 # configurable to however many pixels you have on your led strip
        self.COLORLEN = self.STRIPLEN * 3 #Colorlen is the size of the part of the array containing actual
                                          #color information.
        self.ARRAYLEN = self.COLORLEN + 3 #Arraylen is the size of the whole array.
        #the extra 3 pixels are for zeros to reset the array. For some reason
        #the second set of lights takes two zeros to reset completely...
        #The first set only takes one.
        self.lights = bytearray([0x80 for x in range(self.ARRAYLEN)])
        self.lights[0] = 0
        self.lights[self.ARRAYLEN-1] = 0
        self.lights[self.ARRAYLEN-2] = 0
        self.DEV = '/dev/spidev1.0'
        self.spidev = open(self.DEV, 'wb')
        self.allow_anim = 0
        self.allow_timer = True
        self.dither()
        self.periodicRefresh(600)

    def dither():
        #This is probably not the best way to do this.
        #But it works, and it only runs once.
        edges=[1,44,53,61,68,73,78,83,87,92]
        numsteps=[edges[x+1]-edges[x] for i in range(len(edges)-1)]
        self.dither = [] #contains number of off pixels
        edge=0
        i_numsteps=0
        for inputVal in range(1,92):
            if inputVal >= edges[edge+1]:
                edge+=1
                i_numsteps+=1
            ns = numsteps[i_numsteps]
            pixels_on = int(self.STRIPLEN*inputVal/ns)
            pixels_off=self.STRIPLEN-pixels_on
            off = []
            for i in range(pixels_off):
                off.append(int((i+1)*self.STRIPLEN/(pixels_off+1)))
            self.dither.append(off)

    def write(self, red,green,blue):
        self.allow_anim = 0
        r_off=[]
        g_off=[]
        b_off=[]
        #print('set anim 0')
        if red < 92:
            r_off=self.dither[red]
        if green < 92:
            g_off=self.dither[green]
        if blue < 92:
            b_off=self.dither[blue]

        for x in range(self.STRIPLEN):
            blue1,green1,red1 = blue,green,red
            if x in b_off:
                blue1-=1
            if x in g_off:
                green1-=1
            if x in r_off:
                red1-=1
            self.setpixel((red1,green1,blue1), x)
        #print('outputting solid color')
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
        #self.spidev.close()
        #Not really needed, the OS will take care of it :)
    def animate(self, animationName, cond):
        self.animation = animations.getAnimator(animationName,self.STRIPLEN)
        self.allow_anim += 1
        self.animupdate(self.allow_anim,cond)
    def animupdate(self,anim_ID,cond):
        if self.allow_anim == anim_ID:
            #print('anim allowed, updating')
            with(cond):
                self.animation.update()
                l = self.animation.getLights()
                if self.animation.needsRaw():
                    for i,rgb in enumerate(l):
                        self.setrawpixel(rgb,i)
                else:
                    for i,rgb in enumerate(l):
                        self.setpixel(rgb,i)
                #print('pushing anim output')
                self.output()
                self.anim = Timer(0.03,self.animupdate,args=[anim_ID,cond])
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
        with(self.cond):
            while self.keepGoing:
                if self.message != "":
                    self.processMessage()
                self.cond.wait()
        
                
    """
    Posts a message and tells the run method to process it.
    """
    def sendMessage(self, data):
        with(self.cond):
            self.message = data.strip()
            self.cond.notifyAll()
    def messageOverride(self, data):
        with(self.cond):
            self.message = data
            self.cond.notifyAll()

    def stop(self):
        with(self.cond):
            self.keepGoing = False
            self.cond.notifyAll()
            self.lights.stop()


    def processMessage(self):
        if self.message.split('.')[0] == 'anim':
            try:
                self.lights.animate(self.message.split('.')[1],self.cond)
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
                print(traceback.format_exc())
        
