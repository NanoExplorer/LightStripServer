
import socket, time

UDP_IP = "10.0.0.33"
UDP_PORT = 12625

sock = socket.socket(socket.AF_INET, #internet
                     socket.SOCK_DGRAM) #UDP
for x in [x for x in range(50)]:
    message = "This is packet number " + str(x)
    sock.sendto(message, (UDP_IP, UDP_PORT))
    #time.sleep(.5)
