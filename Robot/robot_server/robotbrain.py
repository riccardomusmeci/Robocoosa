from A_star import AStar
import time 

class RobotBrain(object):
    '''
    E' la classe che si occupa della parte decisionale del robot.
    
    Attributi:
        reply (dict): e' un dizionario che contiene l'azione che il robot deve compiere. 
                      In futuro sono previsti ampliamenti per la fase di avvicinamento ad un oggetto
        heading (stringa): indica dove punta il davanti del robot
        startPosition (tupla): indica la posizione iniziale del robot
        goalPosition (tupla): indica la posizione finale del robot
        astar (AStar): e' l'attributo che lancia una ricerca A Star sulla mappa a disposizione
        stepsToGoal (list): lista di celle che il robot deve attraversare per arrivare al goal
        newStartForAStar (tupla): nuova posizione iniziale del robot, che deve raggiungere
    '''

    def __init__(self):
        self.heading = "davanti"
        self.startPosition = (9, 0)
        self.goalPosition = (0, 9)
        self.reply = None
        self.astar = AStar()
        self.initAStar()
        self.newStartForAStar = None
        
    
    def initAStar(self):
        '''
        Metodo che inizializza le strutture dati per la ricerca A star
        '''
        self.astar.mappa.initCells([], self.startPosition, self.goalPosition)
        self.stepsToGoal = []
    
    def analyzeData(self, dati):
        '''
        Metodo che analizza i dati sensoriali che gli arrivano dal robot

        @param dati (str): stringa di caratteri che contiene i dati sensoriali (viene convertita in dict)
        '''
        print "Sono dentro analyzeData"
        datiSensoriali = eval(dati)
        print datiSensoriali
        
        '''
        Con self.takeDecision(...), ottengo la prossima cella da visitare e la memorizzo
        in self.newStartForAStar
        '''
        self.takeDecision(datiSensoriali)
        move = self.understandMoveToDo()
        if move is None:
            print "QUALCHE PROBLEMA IN FASE DI PROGETTAZIONE"
            return None

        self.reply = {
            "azione": "movimento",
            "direzione": move
        }
        
        print "Adesso il robot punta verso ", self.heading
        self.startPosition = self.newStartForAStar
                
    
    
    def takeDecision(self, datiSensoriali):
        '''
        Metodo che esegue AStar, ottenendo, in base ai dati sensoriali, 
        la prossima mossa da fare.

        @param datiSensoriali (dict): dizionario contenente i dati sensoriali
        '''
        print "Il robot punta verso ", self.heading
        datiSensorialiFromHeading = self.modifyDataBecauseHeading(datiSensoriali)
        print datiSensorialiFromHeading
        ostacoli = self.astar.percepisciOstacoli(self.newStartForAStar, datiSensorialiFromHeading)
        print ostacoli
        self.astar.mappa.setOstacoli(ostacoli)
        self.astar.mappa.printMappa()
        self.astar.search()
        self.newStartForAStar = (self.astar.pathToGoal[0].x, self.astar.pathToGoal[0].y)
        new_goal = None
        self.astar.recharge(self.newStartForAStar, new_goal)
        
   
    def modifyDataBecauseHeading(self, datiSensoriali):
        '''
        Metodo che aggiusta i dati sensoriali in base a dove punta il davanti del robot, specificato da heading.abs

        @param datiSensoriali (dict): dizionario contenente i dati sensoriali

        @returns un dizionario contenente le informazioni dei sonar davanti, dietro, destra e sinistra in base al heading
        '''

        if self.heading == "davanti":
            return {
                'davanti': datiSensoriali["sonar_centro"],
                'dietro': None,
                'destra': datiSensoriali["sonar_destra"],
                'sinistra': datiSensoriali["sonar_sinistra"]
            }
        
        if self.heading == "destra":
            destra = datiSensoriali["sonar_centro"]
            dietro = datiSensoriali["sonar_destra"]
            davanti = datiSensoriali["sonar_sinistra"]
            return {
                'davanti': davanti,
                'dietro': dietro,
                'destra': destra,
                'sinistra': None
            }
            
        if self.heading == "sinistra":
            sinistra = datiSensoriali["sonar_centro"]
            dietro = datiSensoriali["sonar_sinistra"]
            davanti = datiSensoriali["sonar_destra"]
            return {
                'davanti': davanti,
                'dietro': dietro,
                'destra': None,
                'sinistra': sinistra
            }
        if self.heading == "dietro":
            return {
                'dietro': datiSensoriali["sonar_centro"],
                'davanti': None,
                'sinistra': datiSensoriali["sonar_destra"],
                'destra': datiSensoriali["sonar_sinistra"]
            }
    
    
    def understandMoveToDo(self):
        '''
        Metodo che restituisce la mossa da fare in base alla posizione attuale e la prossima da raggiungere

        @returns move (str): stringa che puo' essere 'avanti', 'destra', 'sinistra'
        '''
        x = self.newStartForAStar[0] - self.startPosition[0]
        y = self.newStartForAStar[1] - self.startPosition[1]
        print "Differenza fra la posizione iniziale, " + str(self.startPosition) + " e la successiva," + str(self.newStartForAStar) + " e': ", (x, y)
        move = None
        if self.heading == "davanti":
            print "Sono in davanti, cerco di capire la mossa"
            if x<0:
                move = "davanti"
                self.heading = "davanti"
            if y<0:
                move = "sinistra"
                self.heading = "sinistra"
            if y>0:
                move = "destra"
                self.heading = "destra"
            print move
            return move
        if self.heading == "destra":
            print "Sono in destra, cerco di capire la mossa"
            if y>0:
                move = "davanti"
                self.heading = "destra"
            if x>0:
                move = "destra"
                self.heading = "dietro"
            if x<0:
                move = "sinistra"
                self.heading = "davanti"
            print move
            return move
        if self.heading == "sinistra":
            print "Sono in sinistra, cerco di capire la mossa"
            if y<0:
                move = "davanti"
                self.heading = "sinistra"
            if x<0:
                move = "destra"
                self.heading = "davanti"
            if x>0:
                move = "sinistra"
                self.heading = "dietro"
            print move
            return move
        if self.heading == "dietro":
            print "Sono in dietro, cerco di capire la mossa"
            if x>0:
                move = "davanti"
                self.heading = "dietro"
            if y<0:
                move = "destra"
                self.heading = "sinistra"
            if y>0:
                move = "sinistra"
                self.heading = "destra"
            print move
            return move
        return move
                


