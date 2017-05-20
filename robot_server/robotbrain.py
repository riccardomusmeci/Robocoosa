'''
Questa classe permette al robot di compiere decisioni in base ai dati che riceve dai sensori
Attributi:
    - sonar: contiene il valore, in cm, della distanza dell'ostacolo dal robot
    - IR: e' un booleano che indica la presenza vicina di ostacoli
    - decision: e' il dizionario che contiene le azioni che il robot deve compiere
Metodi:
    - analyzeData: riceve in input un dizionario e aggiorna i dati che ha del mondo
    - getDecision: metodo che in base ai dati che si hanno del mondo, prende una decisione e la restituisce
'''

class RobotBrain(object):

    def __init__(self):
        print "Cervello del robot inizializzato..."
        # in futuro potremmo inizializzare mappe e dati sensoriali, in modo tale da avere dei metodi che operano sui dati costantemente aggiornati
        self.sonar = -1
        self.IR = -1
        self.decision = {
            "forward" : 1, #bool
            "back" : 0, #bool
            "right": 1, #bool
            "left": 0, #bool
            "rotate": 0 #gradi
        }

    '''
    Questo metodo prende in input i dati passatogli (nella nostra implementazione e' il server che glieli passa) e
    li analizza in modo tale da decidere che azione intraprendere.
    Parametri:
        - data: deve essere di tipo dizionario (JSON);
    '''
    def analyzeData(self, data):
        print data
        print "aggiorno i dati del mondo..."
        self.sonar = data['sonar']
        self.IR = data['IR']


    def getDecision(self):
        if self.IR == 0 and self.sonar > 40:
            self.decision['forward'] = 1
            self.decision['right'] = 0

        return str(self.decision)
