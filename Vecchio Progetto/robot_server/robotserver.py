import socket
import sys
from robotbrain import RobotBrain

'''
Questa classe gestisce la connessione con il robot tramite WiFi e usando una connessione TCP.
Attributi:
    - HOST: rappresenta l'indirizzo IP del server (e' una costante);
    - PORT: rappresenta la porta di ascolta della socket;
    - s: rappresenta la socket;
    - robotBrain: e' un'istanza della classe RobotBrain che si occupa di determinare le mosse che il robot deve fare
Metodi:
    - init: inizializza gli attributi e aggancia il server alla socket
    - bindSocket: aggancia la socket all'host e alla porta specificata
    - listen: permette al server di accettare connessioni in ingresso (max 2) e, analizzando le richieste che gli arrivano
              sottoforma di pacchetti JSON, fa decidere al brain del robot che azioni compiere, per poi mandargliele
    - start: semplicemente chiamo la listen e quando questa termina, chiudo la socket
'''

class RobotServer(object):
    def __init__(self):
        self.HOST = '192.168.0.104'
        self.PORT = 1931
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # in order to prevent the "address already in use" error
        # aggancio la socket
        self.bindSocket()
        self.robotBrain = RobotBrain()

    '''
    Questo metodo aggancia la socket all'host e alla porta specificata
    '''
    def bindSocket(self):
        try:
            # binding the socket to the specified host and port
            self.s.bind((self.HOST, self.PORT))
        except socket.error, msg:
            print 'Bind failed. Error code: ' + str(msg[0]) + ' message ' + msg[1]
            sys.exit()
        print "Socket agganciata correttamente"

    '''
    Questo metodo permette al server di mettersi in ascolto sulla socket
    '''
    def listen(self):
        '''
        In futuro il numero di connessioni in ascolto sara' 2, una per Arduino e una per la Camera
        '''
        self.s.listen(1)
        print "Il server si e' messo in ascolto"

        while True:
            conn, addr = self.s.accept()
            data = conn.recv(256)
            data = eval(data) #data ora e' un dizionario (JSON)
            if not data:
                print "Non ho ricevuto nessun dato"
                break
            self.robotBrain.analyzeData(data)

            reply = self.robotBrain.getDecision()
            conn.sendall(reply)

        conn.close()

    def start(self):
        self.listen()
        self.s.close()
