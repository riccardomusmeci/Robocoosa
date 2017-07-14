import socket
import sys
from robotbrain import RobotBrain

class Robot(object):

    def __init__(self):
        print "Init server"
        self.HOST = "192.168.0.100"
        self.PORT = 1931
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        '''
        Riga di codice usata per evitare l'errore "address already in use"
        '''
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.bindSocket()
        '''
        Inizializzo il cervello del robot che si occupa della parte decisionale
        '''
        self.brain = RobotBrain()


    def bindSocket(self):
        '''
        Metodo che fa il binding della socket
        '''
        try:
            '''
            Binding della socket ad host e alla porta
            '''
            self.socket.bind((self.HOST, self.PORT))
        except socket.error, message:
            print "Bind fallito. Codice di errore: " + str(message[0]) + ", messaggio: " + message[1]
            sys.exit()
        print "Socket agganciata correttamente"

    def listen(self):
        '''
        Metodo che permette al server di mettersi in ascolto di eventuali connessioni
        '''
        self.socket.listen(2)
        print "Il server si e' messo in ascolto"

        while True:
            connessione, indirizzo = self.socket.accept()
            print "Connessione da ", indirizzo
            dati = connessione.recv(256)
            dati = eval(dati)
            self.brain.analyzeData(dati)
            connessione.sendall(str(self.brain.reply))

        connessione.close()

    def start(self):
        '''
        Metodo che fa partire il robot
        '''
        self.listen()
        self.socket.close()
