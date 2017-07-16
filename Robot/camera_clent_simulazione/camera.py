# Python TCP Client A
import socket
import time

host = '192.168.0.100'
port = 1931
BUFFER_SIZE = 2048

startTime = time.time()
dati = {
    'ID': 'Camera',
    'differenza_angolo': 20
    }

tcpClientA = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpClientA.connect((host, port))

tcpClientA.send(str(dati))
# while time.time() - startTime < 60:
#     print "Waiting.."
print "sto chiudendo la connessione"
tcpClientA.close()

    

