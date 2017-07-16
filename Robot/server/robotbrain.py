import numpy as np

DA_INIZIO_AD_OGGETTI = 100
DA_OGGETTI_AD_AREA_ROSSA = 300
DA_AREA_ROSSA_AD_OGGETTI = 0 
DA_OGGETTI_AD_AREA_BLU = 0
DA_AREA_BLU_AD_OGGETTI = 0
DA_OGGETTI_AD_AREA_GIALLA = 0
DA_AREA_GIALLA_AD_OGGETTI = 0

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
        self.datiSensoriali = {}
        self.datiCamera = {}
        self.constants = [
            DA_INIZIO_AD_OGGETTI, DA_OGGETTI_AD_AREA_ROSSA, DA_AREA_ROSSA_AD_OGGETTI, 
            DA_OGGETTI_AD_AREA_BLU, DA_AREA_BLU_AD_OGGETTI,
            DA_OGGETTI_AD_AREA_GIALLA, DA_AREA_GIALLA_AD_OGGETTI,
        ]
        self.reply = {}
        self.numeroDiAvantiPrimaDiRiorentarsi = 0
        
        self.doveInMacchinaAStatiFiniti = 0
        self.ANGOLOTARGET = self.constants[self.doveInMacchinaAStatiFiniti]

    def takeDecision(self, dati):

        if dati["ID"] == "Camera":
            self.datiCamera = dati
            print "\n"
            print "ARRIVATI DATI DA CAMERA, IDENTIFICATO L'AREA/OGGETTO"
            print self.datiCamera
            print "Imposto la modalita del robot in avvicinamento"
            print "\n"
            self.modalita = "avvicinamento"
        
        if dati["ID"] == "Arduino":
            print "Il robot e' in modalita: ", self.modalita
            self.datiSensoriali = dati
            #print self.datiSensoriali
        
        if self.datiSensoriali["vengoDa"] == -1:
            print "Il robot e' in modalita' avvicinamento, devo lasciarlo lavorare"
            return
        self.takeDecisionForArduino()
    
    
    def takeDecisionForArduino(self):

        if self.modalita == "init":
            print "Sono in modalita' init"
            self.reply = {
                "comando": 0, 
                "angolo_target": self.ANGOLOTARGET,
                "verso_rotazione": self.determinaOrientamento()
            }
            self.modalita = "movimento"
            return

        if self.miDevoOrientare() is True:
            return

        if self.modalita == "movimento":
            self.reply = {
                "comando": 1,
                "ruota_sx": 160,
                "ruota_dx": 160
            }
            return

        if self.modalita == "avvicinamento":
            (angolo_target, verso) = self.calcolaAngoloDaRaggiungereDataUnaDifferenzaFraAngoli(self.datiCamera["differenza_angolo"])
            
            self.reply = {
                "comando": 2,
                "angolo_target": angolo_target,
                "verso_rotazione": verso,
                "ruota_sx": 120,
                "ruota_dx": 120
            }
            if self.datiSensoriali["vengoDa"] == -1:
                self.doveInMacchinaAStatiFiniti += 1
                self.ANGOLOTARGET = self.constants[self.doveInMacchinaAStatiFiniti]
                self.modalita = "init"
                print "Pronto per raggiungere un'altra area, devo avere un angolo di ", self.ANGOLOTARGET
            else:
                print "Il robot si sta avvicinando all'oggetto/area, non lo disturbo"
            return
        
        if self.modalita == "fermo":
            self.reply = {
                "comando": 3,
            }
            return

    def miDevoOrientare(self):
        if self.numeroDiAvantiPrimaDiRiorentarsi == 15:
            #devo trovare un algoritmo che mi permette di riorientarmi in base alla bussola e all'angolo target
            verso = self.determinaOrientamento()
            self.reply = {
                "comando": 0,
                "angolo_target": self.ANGOLOTARGET,
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
        differenza_angoli = int(angolo_attuale - self.ANGOLOTARGET)
        if differenza_angoli in np.arange(-10, 10, 1):
            print "Il robot non deve ruotare, e' orientato abbastanza bene"
            return -1
        if differenza_angoli in np.arange(-1, -self.ANGOLOTARGET, 1) or differenza_angoli in np.arange(180, 360-self.ANGOLOTARGET, 1):
            print "Il robot deve girare verso sx per mantenere l'orientamento"
            return 1
        else:
            print "Il robot deve girare verso dx per mantenere l'orientamento"
            return 0

    def calcolaAngoloDaRaggiungereDataUnaDifferenzaFraAngoli(self, differenza_angolo):
        verso = -1
        if differenza_angolo < 0:
            verso = 0
        else:
            verso = 1
        angolo_target = self.datiSensoriali["buss"] + differenza_angolo
        
        if angolo_target > 360:
            angolo_target -= 360
        if angolo_target < 0:
            angolo_target += 360
        
        return (angolo_target, verso)
        
