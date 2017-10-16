
import socket, time

UDP_IP = "10.0.0.33"
UDP_PORT = 12625

sock = socket.socket(socket.AF_INET, #internet
                     socket.SOCK_DGRAM) #UDP
for x in [float(x+1) ** float(x+1) for x in range(50)]:
    prefix = "ALT:"
    message = prefix + str(x)
    sock.sendto(message, (UDP_IP, UDP_PORT))
    print message
    time.sleep(.5)
