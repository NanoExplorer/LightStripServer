LightStripServer
================

Will allow remote control of a raspberry pi running an AdaFruit Digital Addressable RGB LED light strip.

Currently this is highly specalized to the KSP mod that I'm designing - the client sends UDP messages to the PI specifying the altitude of the ship above the surface of the planet. The raspberry pi uses that information to display the position of the ship on the light strip as a yellow dot. When I am done, the pi will also have a voiceover that narrates scale changes such as "Scale changed to 32 meters for final descent" or "Radar lock acquired" 

It will be fun.
