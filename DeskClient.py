
import socket, time, argparse

def parseCmdArgs(argumentList,helpList,typeList):
    """Parses command-line arguments. Useful for moving away from the galaxy.py universal interface
    because it takes so much time to start up, and has to import everything. 
    """
    parser = argparse.ArgumentParser()
    for argument,theHelp,theType in zip(argumentList,helpList,typeList):
        if theType == 'bool':
            parser.add_argument(*argument,help=theHelp,action='store_true')
        else:
            parser.add_argument(*argument,help=theHelp,type=theType)
    return parser.parse_args()

args = parseCmdArgs([["red"],["green"],["blue"]],
             ["red value","green value","blue value"],
             [int,int,int])
r=args.red
g=args.green
b=args.blue

IP = "64.189.142.106"
PORT = 12625

sock = socket.socket(socket.AF_INET, #internet
                     socket.SOCK_STREAM) #UDP

message = bytes("{}:{}:{}".format(r,g,b),"UTF-8")
sock.connect((IP,PORT))
sock.send(message)
sock.close()

#time.sleep(.5)
