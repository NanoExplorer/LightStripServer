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
import DeskLogicThread
import sys
import signal


#feel free to change these values
IP = "0.0.0.0"
PORT = 12625


worker = DeskLogicThread.WorkerThread()

def signal_handler(signal, frame):
    print("You pressed CTRL-C! Exiting...")
    worker.stop()
    sys.exit(1)
    
signal.signal(signal.SIGINT, signal_handler)


def main():
    sock = socket.socket(socket.AF_INET, #internet
                         socket.SOCK_STREAM) #UDP
    sock.bind((IP, PORT))
    s.listen(0)
    while True:
        conn, addr = s.accept()
        while True:
            data = conn.recv(20) #apparently "buffer size" is 20 bytes. Don't know how that will affect me
            if not data: break
            worker.sendMessage(data)
            print("Received: {}".format(str(data)))
        conn.close()
if __name__ == "__main__":
    main()


