"""This python file should be run on a Raspberry pi with a set up similar to
the adafruit light painting tutorial at:
https://learn.adafruit.com/light-painting-with-raspberry-pi/hardware

Light strip DI port connected to rpi MOSI port and
light strip CI port connected to rpi SCLK port.

The raspberry pi must have hardware SPI kernel support (definitely works with
Occidentalis, but might not work with default Wheezy.

Starts a websocket server on port 8765 (configurable) and listens for data.

"""
import sys
import logging
logging.basicConfig(format='%(asctime)s %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level=logging.INFO,
                    filename="/var/log/desklight.log")
root = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
root.addHandler(ch)
import time
import socket
import websockets
import dropbox
import DeskLogicThread
import signal
import asyncio

#feel free to change these values
IP = "0.0.0.0"
PORT = 8765

def save_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    with open('secret','r') as sf:
        token = sf.read()
        #Dear future me: DON'T PUT THE DROPBOX KEY INTO THE SOURCE CODE AND PUSH IT TO GH.
    dbclient = dropbox.Dropbox(token)
    dbclient.files_upload(str.encode(ip),'/ip_zeropi.txt',mode=dropbox.files.WriteMode('overwrite'))


def signal_handler(signal, frame):
    logging.info("You pressed CTRL-C! Exiting...")
    worker.stop()
    sys.exit(1)

def redlight():
    stuff="30:0:0"
    #30 is the lowest level of red. Set it any lower and it'll be off. I promise :)
    worker.sendMessage(stuff)
    while True:
        time.sleep(700)

@asyncio.coroutine
def rcv_color(websocket,path):
    
    # with socket.socket(socket.AF_INET, #internet
    #                      socket.SOCK_STREAM) as sock: #TCP
        # sock.bind((IP, PORT))
        # sock.listen(1)
        # while True:
        #     conn, addr = sock.accept()
    addr=websocket.remote_address[0]
    logging.info("Connection established with {}.".format(addr))
    while True:
        try:
            data = yield from websocket.recv() 
            try:
                worker.sendMessage(data)
                logging.info("Received: {}".format(data))
            except:
                logging.warning("Received malformed data: {}".format(data))
        except websockets.exceptions.ConnectionClosed:
            logging.info("Lost connection with {}.".format(addr))
            break
    # conn.close()
    # logging.info("Connection closed.")
def main():
    logging.info("Server starting.")
    start_server=websockets.serve(rcv_color,IP,PORT)

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == "__main__":
    try:    
        #save_ip_address()
        worker = DeskLogicThread.WorkerThread()    
        worker.messageOverride("anim.fireworks")
        signal.signal(signal.SIGINT, signal_handler)   
        
        main()
        #redlight()
    finally:
        worker.stop()

