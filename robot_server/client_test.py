import socket
import sys

try:
    #create an AF_INET, STREAM socket (TCP)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error, msg:
    print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message: ' + msg[1]
    sys.exit()

# If I can create the socket
print "Socket created"

host = '192.168.1.11'
port = 1931

try:
    remote_ip = socket.gethostbyname(host)
except socket.gaierror:
    #could not resolve
    print "Hostname could not be resolved. Exiting"
    sys.exit()

print 'Ip address of ' + host + ' is ' + remote_ip

#connect to remote server
s.connect((remote_ip, port))

print 'Socket Connected to ' + host + ' on ip ' + remote_ip

# send some data to remote server
message = {
    'id': "Arduino",
    'sonar': 50,
    'IR': 0
}

try:
    # set the whole string
    s.sendall(str(message))
except socket.error:
    #send failed
    print "Send failed"
    sys.exit()

print "message send successfully"

#receiving data
reply = s.recv(4096)
print "*****REPLY*****"
print reply

s.close()
print "socket has been close"
