import socket
import sys
import numpy as np
import constants as c
from framesgrabber import FramesGrabber
from imutils.video import WebcamVideoStream
from imutils.video import FPS
from object import Object
import argparse
import imutils
import math
import cv2

class Robot(object):

    def __init__(self):
        print "Init server"
        self.HOST = "192.168.0.101"
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
        self.modalita = "movimento"
        self.datiSensoriali = {
            "ID": None,
            "IR_dx": -1,
            "IR_sx": -1,
            "IR_cdx": -1,
            "IR_c": -1,
            "IR_csx": -1,
            "IR_t": -1,
            "IR_b": -1,
            "IR_bsx": -1,
            "IR_bdx": -1,
            "buss": -1,
            "vengoDa": -1
        }

        self.costantiFSM = [c.DA_INIZIO_AD_OGGETTI, c.DA_OGGETTI_AD_AREA_ROSSA, c.DA_AREA_ROSSA_AD_OGGETTI, c.DA_OGGETTI_AD_AREA_BLU, c.DA_AREA_BLU_AD_OGGETTI, c.DA_OGGETTI_AD_AREA_GIALLA, c.DA_AREA_GIALLA_AD_OGGETTI]
        self.indiceFSM = 0
        self.angoloTarget = self.costantiFSM[self.indiceFSM][0]
        self.reply = {}
        self.numeroDiAvantiPrimaDiRiorientarsi = 0

        self.address = "rtsp://192.168.0.100:554/live/ch00_0"
        self.vs = WebcamVideoStream(src=self.address).start()
        self.fps = FPS().start()

        # dati camera
        self.oggettoRosso = Object("red")
        self.oggettoBlu = Object("blue")
        self.oggettoGiallo = Object("giallo")
        
        self.trovaOggetto = 0
        self.presaRilascio = 0
        self.trovaArea = 0
        self.oggettoPreso = 0
        
        self.versoRotazione = -1
        self.differenza_angolo = 0
        self.hsv = None

        self.center_frame_x = None
        self.center_frame_y = None

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
            connessione = None
            try:
                connessione, indirizzo = self.socket.accept()
                print "Connessione da ", indirizzo
                if connessione:
                    dati = connessione.recv(256)
                    dati = eval(dati)
                    self.takeDecision(dati)

                    connessione.send(str(self.reply))

            except KeyboardInterrupt:
                if connessione:  
                    connessione.close()
                    # do a bit of cleanup
                cv2.destroyAllWindows()
                self.vs.stop()
                break  

    def start(self):
        '''
        Metodo che fa partire il robot
        '''
        self.listen()
        self.socket.close()

    def takeDecision(self, dati):
        '''
        Questo metodo prende in input i dati che mandano Arduino e Camera, e salva i dati nelle corrispettive strutture dati

        @param dati (dict): dizionario contenente i dati del mondo visti da Arduino/Camera

        '''
        frame = self.vs.read()

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
 
	    # update the FPS counter
        self.fps.update()

        self.elaboraFrame(frame)
        self.analyzeDataFromCamera()

        if dati["ID"] == "Arduino":
            self.datiSensoriali = dati
            self.FSM()
            self.infoStatoDelMondo()

    def analyzeDataFromCamera(self):
        '''
        Questo metodo permette di analizzare i dati che arrivano dalla camera, e di conseguenza settare una modalita' (ovvero avanzare nella FSM) per il robot.
        '''
        print "trovaOggetto: ", self.trovaOggetto
        print "trovaArea: ", self.trovaArea
    
        if (self.trovaOggetto == 1 or self.trovaArea == 1) and self.modalita == "movimento":
            print "Sono in modalita avvicinamento"
            self.modalita = "avvicinamento"
            return

        if self.presaRilascio == 1 and self.modalita == "avvicinamento":
            self.modalita = "presa-rilascio"
            self.presaRilascio = 0
            self.oggettoPreso = 1
            return

    def FSM(self):
        '''
        Questo metodo rappresenta la FSM che fa avanzare il robot nel mondo.
        '''
        
        ruota_sx = 0
        ruota_dx = 0
        con_oggetto = 1          #da modificare quando si aggiungeranno gli IR
        if self.indiceFSM%2 == 0:
            con_oggetto = 0
        print "con_oggetto: ", con_oggetto 
        if self.modalita == "init":
            print "[INIT] Angolo da raggiungere: ", self.angoloTarget
            self.reply = {
                "comando": 0,
                "sterzatura_preferita": self.costantiFSM[self.indiceFSM][1],
                "con_oggetto": con_oggetto,
                "angolo_target": self.angoloTarget,
                "verso_rotazione": self.determinaOrientamento()
            }
            self.modalita = "movimento"
            print "Posso impostare la modalita movimento adesso"
            return
        
        if self.miDevoOrientare(con_oggetto) is True:
            return
    
        if self.modalita == "movimento": 
            ruota_sx = 190
            ruota_dx = 200  
            self.reply = {
                "comando": 1,
                "con_oggetto": con_oggetto,
                "ruota_sx": ruota_sx + con_oggetto*50,
                "ruota_dx": ruota_dx + con_oggetto*50
            }
            return

        if self.modalita == "avvicinamento":
            if self.verso_rotazione == 0:
                self.differenza_angolo *= -1
            self.angoloTarget = self.determinaAngolo(self.datiSensoriali['buss'] + self.differenza_angolo)
            self.differenza_angolo = 0
            
            ruota_sx = 140
            ruota_dx = 140
            self.reply = {
                "comando": 2,
                "con_oggetto": con_oggetto,
                "angolo_target": self.angoloTarget,
                "verso_rotazione": self.verso_rotazione,
                "ruota_sx": ruota_sx + con_oggetto*50,
                "ruota_dx": ruota_dx + con_oggetto*50
            }
            return

        if self.modalita == "presa-rilascio":
            self.reply = {
                "comando": 3,
                "con_oggetto": con_oggetto
            }
            print "[PRESA-RILASCIO] Sto provando a prendere l'oggetto"
            if self.datiSensoriali["vengoDa"] == 3:
                return
            self.indiceFSM += 1
            self.angoloTarget = self.costantiFSM[self.indiceFSM][0]
            self.modalita = "init"
            print "[PRESA-RILASCIO] Ho preso l'oggetto e mi metto in modalita' init"
            return

    def miDevoOrientare(self, con_oggetto):
        '''
        Questo metodo controlla se il robot si deve orientare di nuovo o meno in base ad alcune informazioni:
        - modalita del robot
        - numero di passi in avanti fatti liberamente
        - incontro con un ostacolo recente

        @returns bool: ritorna True o False in base al fatto che si deve orientare di nuovo o meno 
        '''
        
        if self.modalita == "movimento":
            if self.numeroDiAvantiPrimaDiRiorientarsi == 3:
                self.numeroDiAvantiPrimaDiRiorientarsi = 0
                self.reply = {
                    "comando": 0,
                    "con_oggetto": con_oggetto,
                    "angolo_target": self.angoloTarget,
                    "verso_rotazione": self.determinaOrientamento()
                }
                print "[MOVIMENTO] Mi oriento di nuovo verso l'obiettivo"
                return True
        
            if self.datiSensoriali["vengoDa"] == 0:
                print "Il robot ha identificato un ostacolo, gli do' la possibilita' di fare manovra prima di riorentarsi"
                self.numeroDiAvantiPrimaDiRiorientarsi = 0
                return False
            if self.datiSensoriali["vengoDa"] == 1:
                self.numeroDiAvantiPrimaDiRiorientarsi += 1
                print "Il robot ha la strada libera, gli faccio incrementare il contatore per arrivare ad orientarsi di nuovo, ", self.numeroDiAvantiPrimaDiRiorientarsi
                return False
        
        if self.modalita == "avvicinamento":
            if self.datiSensoriali["vengoDa"] == 0:
                print "Nella fase di avvicinamento il robot ha incontrato un ostacolo, lo faccio camminare in avanti prima di farlo orienare con l'angolo target dato inizialmente"
                self.numeroDiAvantiPrimaDiRiorientarsi = 0
                self.modalita = "movimento"
                self.reply = {
                    "comando": 1,
                    "con_oggetto": con_oggetto,
                    "ruota_sx": 230,
                    "ruota_dx": 220 
                }
                self.angoloTarget = self.costantiFSM[self.indiceFSM][0]
                return False
            return False

    def determinaOrientamento(self):
        '''
        Metodo che determina il verso di rotazione da fare in base all'angolo target da raggiungere

        @returns int: il metodo ritorna 0 se il robot deve ruotare da sx verso dx, 1 se il robot deve ruotare da dx verso sx,
                      -1 se il robot non deve ruotare

        '''
        
        angolo_attuale = self.datiSensoriali["buss"]
        differenza_angoli = int(angolo_attuale - self.angoloTarget)
        if differenza_angoli in np.arange(-10, 10, 1):
            print "Il robot non deve ruotare, e' orientato abbastanza bene"
            return -1
        if differenza_angoli in np.arange(-10, -self.angoloTarget, -1) or differenza_angoli in np.arange(180, 360-self.angoloTarget, 1):
            print "Il robot deve girare verso sx per mantenere l'orientamento"
            return 1
        else:
            if differenza_angoli in np.arange(10, 180, 1):
                print "Il robot deve girare verso dx per mantenere l'orientamento"
                return 0
        return -1

    def determinaAngolo(self, angolo):
        '''
        Questo metodo riporta l'angolo passato come input in mod360

        @param angolo (int): angolo da riportare in mod360

        @returns int: restituisce l'angolo portato in mod360
        '''
        if angolo > 359:
            print "Angolo e' maggiore di 360, lo riporto in mod360"
            return angolo - 359
        if angolo < 0:
            print "Angolo e' minore di 0, lo riporto in mod360"
            return angolo + 359
        return angolo

    def differenzaAngoloRilevante(self, alfa, beta):
        '''
        Metodo che determina la differenza in valore assoluto fra due angoli

        @param alfa (float): angolo
        @param beta (float): angolo

        @returns float: valore assoluto della differenza fra i due angoli
        '''
        
        if abs(beta-alfa)<5:
            return False
        else:
            return True

    def infoStatoDelMondo(self):
        '''
        Metodo che stampa le informazioni sul mondo in base ai dati forniti da Arduino e Camera
        '''

        print "\nStato del robot"
        print "Modalita': ", self.modalita
        print "Indice FSM: ",  self.indiceFSM
        print "Vengo da ", self.datiSensoriali["vengoDa"]
        print "Bussola: ", self.datiSensoriali["buss"]
        print "Angolo target: ", self.angoloTarget
        print "Stato del mondo: \n", self.datiSensoriali
        print "\n"

    def resetCameraVariable(self):
        self.trovaOggetto = 0
        self.presaRilascio = 0
        self.trovaArea = 0
        self.versoRotazione = -1
        self.oggettoPreso = 0

    # distanza tra due punti -> serve a calcolare angolo
    def distance(self, (x1, y1), (x2,y2)):
        dist = math.sqrt((math.fabs(x2-x1))**2+((math.fabs(y2-y1)))**2)
        return dist

    def findColor(self, color):
        print "findColor"
        mask = cv2.inRange(self.hsv, color.lower, color.upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        _,cnts,_ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
        center = None

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            if radius > 12:
                return True

    def findOggetto(self, targetColor):
        print "findOggetto"
        mask = cv2.inRange(self.hsv, targetColor.lower, targetColor.upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        _,cnts,_ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
        center = None

        if len(cnts) > 0 and self.findColor(self.oggettoBlu):
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            
            if radius > 12:
                self.trovaOggetto = 1

    def findArea(self, targetColor):
        print "findArea"
        mask = cv2.inRange(self.hsv, targetColor.lower, targetColor.upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        _,cnts,_ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
        center = None

        if len(cnts) > 0 and not self.findColor(self.oggettoBlu):
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            (center_x, center_y) = center
        
            if radius > 25 and center_y < 100:
                self.trovaArea = 1

    def versoOggetto(self, targetColor):
        print "verso Oggetto"
        mask = cv2.inRange(self.hsv, targetColor.lower, targetColor.upper)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        _,cnts,_ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE)
        center = None

        if len(cnts) > 0:
            c = max(cnts, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            
            if radius > 12:

                if center:
                    (center_x, center_y) = center
                    hypotenuse =  self.distance((center_x,center_y), (self.center_frame_x, self.center_frame_y))
                    horizontal = self.distance((center_x, center_y), (self.center_frame_x, center_y))
                    thirdline = self.distance((self.center_frame_x, self.center_frame_y), (self.center_frame_x, center_y))
                    angle = np.arcsin((thirdline/hypotenuse))* 180/math.pi

                    if (center_y > 280):
                        self.presaRilascio = 1
                    else:
                        self.presaRilascio = 0

                    if center_x < self.center_frame_x:
                        self.differenza_angolo = 90 - angle
                        self.verso_rotazione = 0
                    elif center_x > self.center_frame_x:
                        self.differenza_angolo = 90 - angle
                        self.verso_rotazione = 1

  

    def elaboraFrame(self, frame):
        if frame is None:
            print "Frame is None"
            return

        width = 640 #cap.get(cv2.CAP_PROP_FRAME_WIDTH)   # float
        height = 480 #cap.get(cv2.CAP_PROP_FRAME_HEIGHT) # float
        (self.center_frame_x, self.center_frame_y) = (int((width / 2) - 20), height)
        self.hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        if self.trovaOggetto == 0:
            self.findOggetto(self.oggettoRosso)
        
        if self.trovaOggetto == 1 and self.presaRilascio == 0:
            self.versoOggetto(self.oggettoRosso)

        if self.trovaOggetto == 1 and self.oggettoPreso == 1:
            self.findArea(self.oggettoRosso)

        if self.trovaArea == 1 and self.presaRilascio == 0:
            self.versoOggetto(self.oggettoRosso)

        if self.trovaArea == 1 and self.presaRilascio == 1:
            self.resetCameraVariable()