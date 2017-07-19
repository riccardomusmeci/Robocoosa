import socket
import time

HOST = "192.168.1.116"
PORT = 1931

datiCamera = {
            "ID": "Camera",
            "differenza_angolo": 10,
            "verso_rotazione": 1,
            "presa-rilascio" : 0,
            "target": "oggetto" #puo' essere area/oggetto
        }
counter = 0
while True:
    if counter > 3:
        break
    startTime = time.time()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    client.send(str(datiCamera))
    counter += 1
    client.close()
    while time.time() - startTime < 2:
        print "Waiting.."
