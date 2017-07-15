import numpy as np

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
        self.modalita = "movimento"
        self.datiSensoriali = {
            "IR_dx": -1,
            "IR_sx": -1,
            "IR_cdx": -1,
            "IR_c": -1,
            "IR_csx": -1,
            "IR_t": -1,
            "buss": -1,
        }
        self.BUSSOLA = 100
        self.reply = {}

    def takeDecision(self, dati):
        self.datiSensoriali = dati
        print self.datiSensoriali
        
        if self.modalita == "movimento":
            self.reply = {
                "comando": 1,
                "ruota_sx": 180,
                "ruota_dx": 180
            }
        if self.modalita == "init":
            self.reply = {
                "comando": 0,
                "angolo_target": self.BUSSOLA,
                "verso_rotazione": 1,
                "ruota_sx": 140,
                "ruota_dx": 0
            }
            self.modalita = "movimento"
        
        if self.modalita == "fermo":
            self.reply = {
                "comando": 3,
            }

        if self.modalita == "avvicinamento":
            angolo_target = 270
            verso = 1
            self.reply = {
                "comando": 2,
                "angolo_target": angolo_target,
                "verso_rotazione": verso,
                "ruota_sx": 120,
                "ruota_dx": 120
            }
            self.modalita = "fermo"
        