"""This python file should be run on a Raspberry pi with a set up similar to
the adafruit light painting tutorial at:
https://learn.adafruit.com/light-painting-with-raspberry-pi/hardware

Light strip DI port connected to rpi MOSI port and
light strip CI port connected to rpi SCLK port.

The raspberry pi must have hardware SPI kernel support (definitely works with
Occidentalis, but might not work with default Wheezy.

Starts a UDP server on port 12625 (configurable) and listens for data.

"""
import socket

UDP_IP = "127.0.0.1"
UDP_PORT = 12625

sock = socket.socket(socket.AF_INET, #internet
                     socket.SOCK_DGRAM) #UDP
sock.bind((UDP_IP, UDP_PORT))

while True:
    data, addr = sock.recvfrom(1024) #apparently "buffer size" is 1024 bytes. Don't know how that will affect me
    print "Recieved message:", data, "from", addr
