import numpy as np
import constants as c

class RobotBrain(object):
    '''
    E' la classe che si occupa della parte decisionale del robot

    Attributi:
        modalita (str): e' una stringa che contiene la modalita di lavoro del robot (init, movimento, avvicinamento)
        datiSensoriali (dict): dati sensoriali del mondo che vengono aggiornati da quello che manda il robot
        reply (dict): contiene la risposta del server
        DANGERDISTANCE (int): e' il limite di distanza oltre il quale bisogna virare
    '''
    def __init__(self):
        self.modalita = "init"
        self.datiSensoriali = {
            "ID": None,
            "IR_dx": -1,
            "IR_sx": -1,
            "IR_cdx": -1,
            "IR_c": -1,
            "IR_csx": -1,
            "IR_t": -1,
            "buss": -1,
        }
        
        self.datiCamera = {
            "ID": "Camera",
            "differenza_angolo": None,
            "verso_rotazione": -1
        }

        self.angoloTarget = c.DA_INIZIO_AD_OGGETTI
        self.reply = {}
        self.numeroDiAvantiPrimaDiRiorentarsi = 0

    def takeDecision(self, dati):

        if dati["ID"] == "Arduino":
            self.datiSensoriali = dati
            print self.datiSensoriali
        
        if dati["ID"] == "Camera":
            self.datiCamera = dati
            print self.datiCamera
            self.modalita = "avvicinamento"


        self.takeDecisionForArduino()
    
    
    def takeDecisionForArduino(self):

        print "\nStato del robot"
        print "Modalita': ", self.modalita
        print "Vengo da", c.vengoDaStringa[self.datiSensoriali["vengoDa"]]
        print "Bussola: ", self.datiSensoriali["buss"]
        print "Differenza con angolo target: ", int(self.datiSensoriali["buss"] - self.angoloTarget)
        print "Stato del mondo: \n", self.datiSensoriali
        print "\n"

        if self.modalita == "init":
            self.reply = {
                "comando": 0, 
                "angolo_target": self.angoloTarget,
                "verso_rotazione": self.determinaOrientamento()
            }
            self.modalita = "movimento"
            return

        if self.miDevoOrientare() is True:
            return

        if self.modalita == "movimento":
            self.reply = {
                "comando": 1,
                "ruota_sx": 200,
                "ruota_dx": 210
            }
            return

        if self.modalita == "avvicinamento":
            self.angoloTarget = self.determinaAngolo(self.datiSensoriali['buss'] + self.datiCamera["differenza_angolo"])
            self.reply = {
                "comando": 2,
                "angolo_target": self.angoloTarget,
                "verso_rotazione": self.datiCamera["verso_rotazione"],
                "ruota_sx": 120,
                "ruota_dx": 120
            }
            return
        
        if self.datiSensoriali["vengoDa"] == 3:
            self.modalita = "movimento con oggetto"
        
        if self.modalita == "movimento con oggetto":
            self.reply = {
                "comando": 3,
                "angolo_target": self.angoloTarget,
                "ruota_sx": 200,
                "ruota_dx": 210
            }
            return

    def miDevoOrientare(self):
        if self.numeroDiAvantiPrimaDiRiorentarsi == 7:
            #devo trovare un algoritmo che mi permette di riorientarmi in base alla bussola e all'angolo target
            verso = self.determinaOrientamento()
            self.reply = {
                "comando": 0,
                "angolo_target": self.angoloTarget,
                "verso_rotazione": verso,
            }
            self.numeroDiAvantiPrimaDiRiorentarsi = 0
            return True
        
        if self.datiSensoriali["vengoDa"] == 0:
            print "Il robot ha identificato un ostacolo, gli do' la possibilita' di fare manovra prima di riorentarsi"
            self.numeroDiAvantiPrimaDiRiorentarsi = 0
            return False
        if self.datiSensoriali["vengoDa"] == 1:
            self.numeroDiAvantiPrimaDiRiorentarsi += 1
            print "Il robot ha la strada libera, gli faccio incrementare il contatore per arrivare ad orientarsi di nuovo, ", self.numeroDiAvantiPrimaDiRiorentarsi
            return False

    def determinaOrientamento(self):
        '''
        Determino il verso di rotazione da fare in base all'angolo target da raggiungere
        '''
        
        angolo_attuale = self.datiSensoriali["buss"]
        differenza_angoli = int(angolo_attuale - self.angoloTarget)
        if differenza_angoli in np.arange(-10, 10, 1):
            print "Il robot non deve ruotare, e' orientato abbastanza bene"
            return -1
        if differenza_angoli in np.arange(-10, -self.angoloTarget, -1) or differenza_angoli in np.arange(180, 360-self.angoloTarget, 1):
            print "Il robot deve girare da sx verso dx per mantenere l'orientamento"
            return 1
        else:
            if differenza_angoli in np.arange(10, 180, 1):
                print "Il robot deve girare da dx verso sx per mantenere l'orientamento"
                return 0
        return -1

    def determinaAngolo(self, angolo):
        if angolo > 359:
            return angolo - 359
        if angolo < 0:
            return angolo + 359
