'''
Questa classe permette al robot di compiere decisioni in base ai dati che riceve dai sensori
Attributi:
    - sonar: contiene il valore, in cm, della distanza dell'ostacolo dal robot
    - IRLeft: e' un booleano che indica la presenza vicina di ostacoli a sinistra
    - IRCenter: e' un booleano che indica la presenza vicina di ostacoli al centro
    - IRRight: e' un booleano che indica la presenza vicina di ostacoli a destra
    - decision: e' il dizionario che contiene le azioni che il robot deve compiere;
                i campi di questo dizionario sono:
                    - forward: booleano che dice se muoversi o meno in avanti;
                    - back: booleano che dice se muoversi o meno indietro;
                    - speedLeftWheel: indica la velocita' che deve avere la ruota di sx;
                    - speedRightWheel: indica la velocita' che deve avere la ruota di dx;

Metodi:
    - analyzeData: riceve in input un dizionario e aggiorna i dati che ha del mondo
    - getDecision: metodo che in base ai dati che si hanno del mondo, prende una decisione e la restituisce
'''

class RobotBrain(object):

    def __init__(self):
        # in futuro potremmo inizializzare mappe e dati sensoriali, in modo tale da avere dei metodi che operano sui dati costantemente aggiornati
        self.sonar_c = -1
        self.IR_sx = -1
        self.IR_c = -1
        self.IR_dx = -1
        self.DANGERDISTANCE = 20
        self.decision = {
            "forward" : 0, #bool
            "back" : 0, #bool
            "speedLeftWheel": 0,
            "speedRightWheel": 0,
        }

    '''
    Questo metodo prende in input i dati passatogli (nella nostra implementazione e' il server che glieli passa) e
    li analizza in modo tale da decidere che azione intraprendere.
    Parametri:
        - data: deve essere di tipo dizionario (JSON);
    '''
    def analyzeData(self, data):
        print "\n"
        print "**********DATI SENSORIALI***********"
        print data
        self.sonar_c = data['sonar_c']
        self.IR_sx = data['IR_sx']
        self.IR_dx = data['IR_dx']
        self.IR_c = data['IR_c']


    def getDecision(self):

        if self.IR_sx == 0 or self.IR_dx == 0 or self.IR_c == 0:

            if self.IR_sx == 0 or self.IR_c == 0:
                # il robot ruota da dx verso sx (anche nel caso in cui e' bloccato in centro)
                print "Il robot va indietro e ruota da dx verso sx (ha IR a sx oppure centro occupati)"
                self.decision = {
                    "forward" : 0, #bool
                    "back" : 1, #bool
                    "speedLeftWheel": 0,
                    "speedRightWheel": 125,
                }
            # il robot ruota da sx verso dx
            if self.IR_dx == 0:
                print "Il robot va indietro e ruota da sx verso dx (ha IR a dx occupato)"
                self.decision = {
                    "forward" : 0, #bool
                    "back" : 1, #bool
                    "speedLeftWheel": 140,
                    "speedRightWheel": 0,
                }

        if self.IR_sx == 1 and self.IR_dx == 1 and self.IR_c == 1:

            if self.sonar_c > self.DANGERDISTANCE or self.sonar_c < 1:
                print "Il robot va avanti (sonar ci da' la conferma)"
                # il robot si muove in avanti
                self.decision = {
                    "forward" : 1, #bool
                    "back" : 0, #bool
                    "speedLeftWheel": 120,
                    "speedRightWheel": 155,
                }
            else: # il valore del sonar e' compreso fra 1 e la distanza di soglia che indica un ostacolo
                # il robot dovrebbe vedere se c'e' piu' spazio a sx o a dx per muoversi e poi decidere
                print "*******ATTENZIONE*******"
                print "Il robot deve calcolare le distanze verso sx e dx e decidere dove andare"
                # decido che se sia back che forward sono ad 1 --> ho una fase di studio da parte del robot
                self.decision = {
                    "forward" : 1, #bool
                    "back" : 1, #bool
                    "speedLeftWheel": 0,
                    "speedRightWheel": 0,
                }
                '''
                # il robot ruota piano piano verso sx
                print "Il robot gira verso sx (sonar non ci da' la conferma di andare avanti)"
                self.decision = {
                    "forward" : 1, #bool
                    "back" : 0, #bool
                    "speedLeftWheel": 120, #e' in situazione di pericolo e si muove piano (?)
                    "speedRightWheel": 85,
                }
                '''
        print "\n"
        return str(self.decision)
