"""I'll need to figure out the best interface for these. Is it to have objects for each animation? Or just methods that accept an array and then return the next one? I'll probably want to assume that update methods are called on a predictable clock. Either the logic thread will have to handle that or I'll want to design these methods to look at the time and decide how things should look based on that. Which might not be as bad as I think, especially if I can find a mathematical function to describe the animation (I know I'll be able to do that in the case of the rainbow)."""
import time
import math
import random
#import numpy as np
import colorsys
# def _rgb_component(c,x,h):
#     h = h % 6
#     if h<1 and h>=0:
#         return (c,x,0)
#     elif h<2 and h>=1:
#         return (x,c,0)
#     elif h<3 and h>=2:
#         return(0,c,x)
#     elif h<4 and h>=3:
#         return(0,x,c)
#     elif h<5 and h>=4:
#         return(x,0,c)
#     elif h<6 and h>=5:
#         return(c,0,x)

# def hsvToRgb(h,s,v):
#     """h,s,v are all numbers from 0 to 1"""
#     if s == 0:
#         r = g = b = v
#         return (r,g,b)
#     else:
#         c = v*s
#         x = c*(1-abs((6*h)%2 - 1))
#         r,g,b = _rgb_component(c,x,6*h)#
#         m = v-c
#         return (int((r+m)*255), int((g+m)*255), int((b+m)*255))

def getAnimator(name,length):
    name = name.strip()
    if name == 'rainbow':
        return Rainbow(length)
    if name == 'hyperspace':
        return Hyperspace(length)
    if name == 'strobe':
        return Strobe(length)
    if name == 'fireworks':
        return Fireworks(length)
    if name == 'colorcycle':
        return ColorCycle(length)

def _addTuples(a,b):
    c1 = a[0] + b[0]
    c2 = a[1] + b[1]
    c3 = a[2] + b[2]
    if c1 > 255:
        c1 = 255
    if c2 > 255:
        c2 = 255
    if c3 > 255:
        c3 = 255
    return (c1,c2,c3)

class Animation:
    def __init__(self,length):
        self.arraylen = length
        self.lights = [(0,0,0) for i in range(self.arraylen)]
        self.startTime = time.time()
    def getLights(self):
        return self.lights
    def update(self):
        pass
    def needsRaw(self):
        return False

class Strobe(Animation):
    def __init__(self,length):
        Animation.__init__(self,length)
        self.onLights = [(255,255,255) for i in range(self.arraylen)]
    def update(self):
        t = self.onLights
        self.onLights = self.lights
        self.lights = t
        

class HyperspaceParticle:
    def __init__(self,length):
        self.arraylen = length
        self.speed = 10 #pixels per second See what happens if this is perturbed per particle!
        self.isOdd = self.arraylen %2 == 1
        self.center = self.arraylen // 2
        self.length = length
        self.directionLeft = random.random() < 0.5
        if not self.isOdd:
            self.position = self.center-1 if self.directionLeft else self.center
        else:
            self.position = self.center
    def update(self,delta):
        posd = delta * self.speed
        self.position = self.position - posd if self.directionLeft else self.position + posd
        
    def getPos(self):
        return self.position
        
class Hyperspace(Animation):
    """
    Randomly generated particles are generated at the center of the strip and propagate outwards.

    The particles are approximated by 1 pixel wide white dots.
    """
    def __init__(self,length):
        Animation.__init__(self,length)
        
        self.center = self.arraylen//2
        self.probability = 3 #approx. number of particles to generate per second.
        self.lastUpdateTime = time.time()
        self.particles = []
    def needsRaw(self):
        return True
    def update(self):
        #set up delta time system
        self.lights = [(0,0,0) for i in range(self.arraylen)]
        timeNow = time.time()
        delta = timeNow - self.lastUpdateTime
        self.lastUpdateTime = timeNow
               
        #generate more particles
        if delta * self.probability > random.random():
            self.particles.append(HyperspaceParticle(self.arraylen))
        if len(self.particles) == 0:
            self.particles.append(HyperspaceParticle(self.arraylen))
        for particle in self.particles:
            #display particles
            p = particle.getPos()
            #self.lights[particle.getPos()] = (255,255,255)
            rp_int = int((p % 1) * 255)
            lp_int = 255 - rp_int
            lp = math.floor(p)
            rp = lp + 1
            """
            if p = 15, then rp_int will be 0 and lp_int will be 255
            lp will be 15 and rp will be 16 and 100 percent of the particle's intensity will be in pixel 15

            if p = 14.9 then rp_int will be like 229 and lp_int will be 26
            lp will be 14 and rp will be 15
            most of the intensity will be in pixel 15 still.

            """
            
            if lp >= 0 and lp <self.arraylen:
                self.lights[lp] = _addTuples(self.lights[lp],(lp_int,lp_int,lp_int))
            if rp >= 0 and rp <self.arraylen:
                self.lights[rp] = _addTuples(self.lights[rp],(rp_int,rp_int,rp_int))
            #move particles
            particle.update(delta)
        #remove gone particles
        self.particles = [p for p in self.particles if p.getPos() >-1 and p.getPos() <self.arraylen]

class FireworksParticle:
    def __init__(self,length):
        dieroll = random.random()
        if dieroll < 0.333:
            self.color = "red"
        elif dieroll < 0.666:
            self.color = "blue"
        else:
            self.color = "white"
        self.arraylen = length
        self.speed = 10 #pixels per second See what happens if this is perturbed per particle!
        self.isOdd = self.arraylen %2 == 1
        self.center = self.arraylen // 2
        self.length = length
        self.directionLeft = random.random() < 0.5
        if not self.isOdd:
            self.position = self.center-1 if self.directionLeft else self.center
        else:
            self.position = self.center
    def update(self,delta):
        posd = delta * self.speed
        self.position = self.position - posd if self.directionLeft else self.position + posd
        
    def getPos(self):
        return self.position

class Fireworks(Animation):
    """
    Randomly generated particles are generated at the center of the strip and propagate outwards.

    The particles are approximated by 1 pixel wide white dots.
    """
    def __init__(self,length):
        Animation.__init__(self,length)
        
        self.center = self.arraylen//2
        self.probability = 3 #approx. number of particles to generate per second.
        self.lastUpdateTime = time.time()
        self.particles = []
    def needsRaw(self):
        return True
    def update(self):
        #set up delta time system
        self.lights = [(0,0,0) for i in range(self.arraylen)]
        timeNow = time.time()
        delta = timeNow - self.lastUpdateTime
        self.lastUpdateTime = timeNow
               
        #generate more particles
        if delta * self.probability > random.random():
            self.particles.append(FireworksParticle(self.arraylen))
        if len(self.particles) == 0:
            self.particles.append(FireworksParticle(self.arraylen))
        for particle in self.particles:
            #display particles
            p = particle.getPos()
            #self.lights[particle.getPos()] = (255,255,255)
            rp_int = int((p % 1) * 255)
            lp_int = 255 - rp_int
            lp = math.floor(p)
            rp = lp + 1
            """
            if p = 15, then rp_int will be 0 and lp_int will be 255
            lp will be 15 and rp will be 16 and 100 percent of the particle's intensity will be in pixel 15

            if p = 14.9 then rp_int will be like 229 and lp_int will be 26
            lp will be 14 and rp will be 15
            most of the intensity will be in pixel 15 still.

            """
            if particle.color == 'white':
                if lp >= 0 and lp <self.arraylen:
                    self.lights[lp] = _addTuples(self.lights[lp],(lp_int,lp_int,lp_int))
                if rp >= 0 and rp <self.arraylen:
                    self.lights[rp] = _addTuples(self.lights[rp],(rp_int,rp_int,rp_int))
            elif particle.color == 'red':
                if lp >= 0 and lp <self.arraylen:
                    self.lights[lp] = _addTuples(self.lights[lp],(lp_int,0,0))
                if rp >= 0 and rp <self.arraylen:
                    self.lights[rp] = _addTuples(self.lights[rp],(rp_int,0,0))
            elif particle.color == 'blue':
                if lp >= 0 and lp <self.arraylen:
                    self.lights[lp] = _addTuples(self.lights[lp],(0,0,lp_int))
                if rp >= 0 and rp <self.arraylen:
                    self.lights[rp] = _addTuples(self.lights[rp],(0,0,rp_int))
            #move particles
            particle.update(delta)
        #remove gone particles
        self.particles = [p for p in self.particles if p.getPos() >-1 and p.getPos() <self.arraylen]
            

        
class Rainbow(Animation):
    def __init__(self,length):
        Animation.__init__(self,length)
        self.slowness = 1
    def _rainbow(self,x):
        return x/self.arraylen
    def update(self):
        delta = time.time()-self.startTime
        for i in range(self.arraylen):
            hue = self._rainbow(i+delta/self.slowness)%1
            #if i == 0:
            #    print(hue)
            r,g,b=colorsys.hsv_to_rgb(hue,1,1)
            self.lights[i] = (int(r*255),int(g*255),int(b*255))

class ColorCycle(Animation):
    def __init__(self,length):
        Animation.__init__(self,length)
        self.slowness=30
        self.currHue=0
    def update(self):
        delta=time.time()-self.startTime
        currHue=(delta/self.slowness)%1
        r,g,b=[int(x*255) for x in colorsys.hsv_to_rgb(currHue,1,1)]
        for i in self.arraylen:
            self.lights[i] = (r,g,b)

