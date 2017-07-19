import numpy as np
import constants as c
import time

class RobotBrain(object):
    '''
    E' la classe che si occupa della parte decisionale del robot

    Attributi:
        modalita (str): e' una stringa che contiene la modalita di lavoro del robot. Le modalita' previste sono:
                        - init;
                        - movimento;
                        - avvicinamento;
                        - presa/rilascio oggetto;
        datiSensoriali (dict): dati sensoriali del mondo che vengono aggiornati da quello che manda il robot
        reply (dict): contiene la risposta del server in base alla modalita' in cui si trova il robot. 
                      La risposta del server al client sara' cosi' fatta in base alle modalita':
                      - init:
                            reply = {
                                "comando": 0, 
                                "con_oggetto": 0 o 1
                                "angolo_target": angoloTarget,
                                "verso_rotazione": determinaOrientamento()
                            }
                      - movimento:
                            reply = {
                                "comando": 1,
                                "con_oggetto": 0 o 1,
                                "ruota_sx": 230,
                                "ruota_dx": 220
                            }
                       - avvicinamento:
                            reply = {
                                "comando": 2,
                                "con_oggetto": 0 o 1
                                "angolo_target": angoloTarget,
                                "verso_rotazione": datiCamera["verso_rotazione"],
                                "ruota_sx": 230,
                                "ruota_dx": 220
                            }
                       - presa-rilascio:
                            reply = {
                                "comando": 3,
                                "con_oggetto": 0 o 1
                            }
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
            "vengoDa": -1
        }
        self.datiCamera = {
            "ID": "Camera",
            "differenza_angolo": None,
            "verso_rotazione": -1,
            "presa-rilascio": -1,
            "target": None #puo' essere area/oggetto
        }
        self.constants = [c.DA_INIZIO_AD_OGGETTI, c.DA_OGGETTI_AD_AREA_ROSSA, c.DA_AREA_ROSSA_AD_OGGETTI]
        self.indiceFSM = 0
        self.angoloTarget = self.constants[self.indiceFSM][0]
        '''
        La forma che contiene tutti i tipi di riposta e' la seguente, ne metto uno per tipo di risposta
        '''
        self.reply = {}
        self.numeroDiAvantiPrimaDiRiorentarsi = 0
    
    def takeDecision(self, dati):

        if dati["ID"] == "Arduino":
            self.datiSensoriali = dati
            self.FSM()
            self.infoStatoDelMondo()
        
        if dati["ID"] == "Camera":
            self.datiCamera = dati
            self.analyzeDataFromCamera()
            self.reply = "ok camera"
        

    def analyzeDataFromCamera(self):
        if self.modalita == "presa-rilascio":
            return
        if self.datiCamera["presa-rilascio"] == 1:
            print "Posso prendere l'oggetto"
            self.modalita = "presa-rilascio"
        else:
            print "Individuato l'" + self.datiCamera["target"] + ", mi metto in modalita avvicinamento"
            self.modalita = "avvicinamento"
    
    def FSM(self):

        con_oggetto = 0 #da modificare quando si aggiungeranno gli IR
        if self.indiceFSM%2 == 0:
            con_oggetto = 0
        
        if self.modalita == "init":
            print "[INIT] Angolo da raggiungere: ", self.angoloTarget
            self.reply = {
                "comando": 0,
                "sterzatura_preferita": self.constants[self.indiceFSM][1],
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
            self.reply = {
                "comando": 1,
                "con_oggetto": con_oggetto,
                "ruota_sx": 230,
                "ruota_dx": 220
            }
            return

        if self.modalita == "avvicinamento":
            if self.datiCamera["verso_rotazione"] == 0:
                self.datiCamera["differenza_angolo"] *= -1
            self.angoloTarget = self.determinaAngolo(self.datiSensoriali['buss'] + self.datiCamera["differenza_angolo"])
            self.datiCamera["differenza_angolo"] = 0
            self.reply = {
                "comando": 2,
                "con_oggetto": con_oggetto,
                "angolo_target": self.angoloTarget,
                "verso_rotazione": self.datiCamera["verso_rotazione"],
                "ruota_sx": 230,
                "ruota_dx": 220
            }
            return

        if self.modalita == "presa-rilascio":
            self.reply = {
                "comando": 3,
                "con_oggetto": con_oggetto
            }
            self.indiceFSM += 1
            self.angoloTarget = self.constants[self.indiceFSM]
            self.modalita = "init"
            print "[PRESA-RILASCIO] Mi posso mettere in modalita' init e ricominciare la FSM"
            return


    def miDevoOrientare(self, con_oggetto):
        
        if self.modalita == "movimento":
            if self.numeroDiAvantiPrimaDiRiorentarsi == 7:
                #devo trovare un algoritmo che mi permette di riorientarmi in base alla bussola e all'angolo target            
                self.numeroDiAvantiPrimaDiRiorentarsi = 0
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
                self.numeroDiAvantiPrimaDiRiorentarsi = 0
                return False
            if self.datiSensoriali["vengoDa"] == 1:
                self.numeroDiAvantiPrimaDiRiorentarsi += 1
                print "Il robot ha la strada libera, gli faccio incrementare il contatore per arrivare ad orientarsi di nuovo, ", self.numeroDiAvantiPrimaDiRiorentarsi
                return False
        
        if self.modalita == "avvicinamento":
            if self.datiSensoriali["vengoDa"] == 0:
                print "Nella fase di avvicinamento il robot ha incontrato un ostacolo, lo faccio camminare in avanti prima di farlo orienare con l'angolo target dato inizialmente"
                self.numeroDiAvantiPrimaDiRiorentarsi = 0
                self.modalita = "movimento"
                self.reply = {
                    "comando": 1,
                    "con_oggetto": con_oggetto,
                    "ruota_sx": 230,
                    "ruota_dx": 220 
                }
                self.angoloTarget = self.constants[self.indiceFSM]
                return False
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
            print "Il robot deve girare verso sx per mantenere l'orientamento"
            return 1
        else:
            if differenza_angoli in np.arange(10, 180, 1):
                print "Il robot deve girare verso dx per mantenere l'orientamento"
                return 0
        return -1

    def determinaAngolo(self, angolo):
        if angolo > 359:
            print "Angolo e' maggiore di 360, lo riporto in mod360"
            return angolo - 359
        if angolo < 0:
            print "Angolo e' minore di 0, lo riporto in mod360"
            return angolo + 359
        return angolo

    def differenzaAngoloRilevante(self, alfa, beta):
        if abs(beta-alfa)<5:
            return False
        else:
            return True

    def infoStatoDelMondo(self):
        print "\nStato del robot"
        print "Modalita': ", self.modalita
        print "Indice FSM: ",  self.indiceFSM
        print "Vengo da ", self.datiSensoriali["vengoDa"]
        print "Bussola: ", self.datiSensoriali["buss"]
        print "Angolo target: ", self.angoloTarget
        print "Stato del mondo: \n", self.datiSensoriali
        print "\n"