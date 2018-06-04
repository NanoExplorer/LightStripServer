LightStripServer
================

Will allow remote control of a raspberry pi running an AdaFruit Digital Addressable RGB LED light strip.

Simply open a TCP connection with the PI on the specified port, and send it a message like "40:0:40" which should produce a dim purplish color (message format is "red:green:blue" where each color goes from 0-255.)

I have also coded a few server-side animations, such as "rainbow", "hyperspace", and "strobe". The strobe light is highly annoying, and I do not recommend using it for long periods of time. Hyperspace is kinda cool, but the best animation so far is "rainbow."

There's also an android app that allows remote control, but it might not be in this github repo.


This used to be highly specalized to the KSP mod that I was designing. More recently I have given up the Kerbal Space Program angle of this software. The KSP client would send UDP messages to the PI specifying the altitude of the ship above the surface of the planet. The raspberry pi useed that information to display the position of the ship on the light strip as a yellow dot. I was planning to have the pi do a voiceover that narrateed scale changes such as "Scale changed to 32 meters for final descent" or "Radar lock acquired" 

It will be fun.
