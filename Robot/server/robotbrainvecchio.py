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
            "sonar":-1,
            "IR_dx": -1,
            "IR_sx": -1,
            "IR_cdx": -1,
            "IR_c": -1,
            "IR_csx": -1,
            "IR_b": -1,
            "buss": -1,
        }
        self.comingFrom = "avanti"
        self.stepOltreOstacoli = 0
        self.reply = {}
        self.DANGERDISTANCE = 40
        self.BUSSOLA = 100 # devo inizializzare
        '''
        Per quanto riguarda gli altri angoli abbiamo:
        - angolo verso area verde/blu: 328
        - angolo verso area rossa: 241 
        '''

    def analyzeData(self, dati):
        '''
        Metodo che analizza i dati sensoriali passati come input, prendendo una decisione.

        @param dati (str): stringa di caratteri che contiene i dati sensoriali comunicati dal robot
        '''
        self.datiSensoriali = dati
        print "\n"
        print "DATI SENSORIALI"
        print self.datiSensoriali
        print "\n"
        
        if self.modalita == "movimento":
            self.takeDecision()
        if self.modalita == "init":
            self.initRobot()
    
    def initRobot(self):
        self.modalita = "movimento"
        verso = -1
        differenza_angoli = int(self.datiSensoriali['buss'] - self.BUSSOLA)
        print "La differenza fra l'angolo target e quello finale e': ", differenza_angoli
        if differenza_angoli in np.arange(-10,-100, -1) or differenza_angoli in np.arange(170, 259, 1):
            verso = 1
            print "ruota a sx per metterlo in posizione iniziale"
        else:
            if differenza_angoli in np.arange(10,180, 1):
                verso = 0
                print "ruota a dx per metterlo in posizione iniziale"
        self.reply = {
            'azione': 'rotazione',
            'verso_rot': verso,
            'angolo_target': self.BUSSOLA
        }
        
        
    def takeDecision(self):
        #if self.datiSensoriali["IR_csx"]==1 and self.datiSensoriali["IR_cdx"]==1 and self.datiSensoriali["IR_dx"]==1 and self.datiSensoriali["IR_sx"] == 1:
        if self.datiSensoriali["IR_b"] == 1 and self.datiSensoriali["IR_c"] == 1 and self.datiSensoriali["IR_csx"]==1 and self.datiSensoriali["IR_cdx"]==1 and self.datiSensoriali["IR_dx"]==1 and self.datiSensoriali["IR_sx"] == 1:
            #if self.datiSensoriali["sonar"] < 1150 or self.datiSensoriali["sonar"] < 1 or self.datiSensoriali["sonar"] > self.DANGERDISTANCE :
            '''
            Se la strada e' libera, allora vai sempre avanti
            '''

            #Vedo di quanto deve ruotare il robot, e verso dove, per mantenere la direzione verso gli oggetti
            verso = -1
            differenza_angoli = int(self.datiSensoriali['buss'] - self.BUSSOLA)
            #se l'angolo a cui si trova il robot rispetto a quello target e' buono, allora vai semplicemente avanti
            #altrimenti prima ti aggiusti con una rotazione e dopo riparti
            #if differenza_angoli in np.arange(11, -11, -1):
                #self.comingFrom = "avanti"
            print "Il robot puo' andare avanti liberamente"
            self.reply = {
                'azione': 'movimento',
                'avanti': 1,
                'indietro': 0,
                'v_ruota_sx': 220,
                'v_ruota_dx': 220,
                'angolo_target': self.BUSSOLA, #verso_rot e angolo_ target non sono importanti, li mando per uniformita' di pkt
                'verso_rot': verso
            }
            return
            # else:
            #     if self.comingFrom == "ostacolo":
            #         # if self.stepOltreOstacoli == 3:
            #         #     self.comingFrom = "avanti"
            #         #     self.stepOltreOstacoli = 0
            #         # else:
            #         #     self.stepOltreOstacoli += 1
            #         self.comingFrom = "avanti"
            #         #se vengo da un ostacolo e' inutile che mi oriento di nuovo, piuttosto lo faccio andare avanti
            #         print "Vengo da un ostacolo, dovrei poter ruotare per ritrovare la posizione, ma preferisco prima andare un po' avanti"
            #         self.reply = {
            #         'azione': 'movimento',
            #         'avanti': 1,
            #         'indietro': 0,
            #         'v_ruota_sx': 200,
            #         'v_ruota_dx': 200,
            #         'angolo_target': self.BUSSOLA, #verso_rot e angolo_ target non sono importanti, li mando per uniformita' di pkt
            #         'verso_rot': verso
            #         }
            #         return
                
            #     else:
            #         # il passo precedente e' stato in avanti, quindi mi posso orientare di nuovo
            #         print "Posso riorientarmi verso l'angolo target liberamente"
            #         if self.BUSSOLA == 100:
            #             print "La differenza fra l'angolo target e quello finale e': ", differenza_angoli
            #             if differenza_angoli in np.arange(-10,-100, -1) or differenza_angoli in np.arange(170, 259, 1):
            #                 verso = 1
            #                 print "Il robot ruota a sx per mantere la direzione verso l'obiettivo"
            #             else:
            #                 if differenza_angoli in np.arange(10,180, 1):
            #                     verso = 0
            #                     print "Il robot ruota a sx per mantere la direzione verso l'obiettivo"
            #             self.reply = {
            #                 'azione': 'rotazione',
            #                 'verso_rot': verso,
            #                 'angolo_target': self.BUSSOLA
            #             }
            #             return
        # se arrivo qua vuol dire che ho qualche ostacolo vicino
        self.comingFrom = "ostacolo"   
        
        if (self.datiSensoriali["IR_b"] == 0) and (self.datiSensoriali["IR_dx"] == 0 or self.datiSensoriali["IR_cdx"] == 0):
            print "Il robot ha un ostacolo ad L sulla dx, devo girare indietro con la ruota sx"
            self.reply = {
                'azione': 'movimento',
                'avanti': 0,
                'indietro': 1,
                'v_ruota_sx': 180,
                'v_ruota_dx': 0,
                'angolo': self.BUSSOLA,
            }
            return  
        
        if (self.datiSensoriali["IR_b"] == 0) and (self.datiSensoriali["IR_sx"] == 0 and self.datiSensoriali["IR_csx"] == 0):
            print "Il robot ha un ostacolo ad L sulla sx, devo girare indietro con la ruota dx"
            self.reply = {
                'azione': 'movimento',
                'avanti': 0,
                'indietro': 1,
                'v_ruota_sx': 0,
                'v_ruota_dx': 180,
                'angolo': self.BUSSOLA,
            }
            return 
        
        if self.datiSensoriali["IR_dx"] == 0 or self.datiSensoriali["IR_cdx"] == 0:
            print "Il robot ha un ostacolo sulla dx, devo girare indietro con la ruota sx"
            self.reply = {
                'azione': 'movimento',
                'avanti': 0,
                'indietro': 1,
                'v_ruota_sx': 180,
                'v_ruota_dx': 0,
                'angolo': self.BUSSOLA,
            }
            return   
        
        if self.datiSensoriali["IR_sx"] == 0 or self.datiSensoriali["IR_csx"] == 0:
            print "Il robot ha un ostacolo sulla sx, devo girare indietro con la ruota dx"
            self.reply = {
                'azione': 'movimento',
                'avanti': 0,
                'indietro': 1,
                'v_ruota_sx': 0,
                'v_ruota_dx': 180,
                'angolo': self.BUSSOLA,
            }
            return
        
        if self.datiSensoriali["IR_b"] == 0:
            if self.BUSSOLA == 100:
                print "Il robot ha un ostacolo solo davanti, devo girare indietro con la ruota sx, scelta per l'angolo target ", self.BUSSOLA
                self.reply = {
                    'azione': 'movimento',
                    'avanti': 0,
                    'indietro': 1,
                    'v_ruota_sx': 180,
                    'v_ruota_dx': 0,
                    'angolo': self.BUSSOLA,
                }
                return
