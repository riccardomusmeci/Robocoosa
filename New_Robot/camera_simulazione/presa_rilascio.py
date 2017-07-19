import socket
import time

HOST = "192.168.1.116"
PORT = 1931

datiCamera = {
            "ID": "Camera",
            "differenza_angolo": 0,
            "verso_rotazione": -1,
            "presa-rilascio" : 1,
            "target": "oggetto" #puo' essere area/oggetto
        }

startTime = time.time()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send(str(datiCamera))
client.close()

    
    
