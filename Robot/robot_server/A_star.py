from priority_queue import PriorityQueue
from mappa import Mappa

class AStar():

    def __init__(self):

        self.aperta = PriorityQueue()
        self.chiusa = set()
        self.mappa = Mappa(10, 10, start=(0, 0), goal=(9, 9))

        self.pathToGoal = []

    def recharge(self, new_start, new_goal):
        '''
        Metodo per ricare le strutture dati utili per il calcolo del percorso piu' breve

        @param new_start: tupla contenente le coordinate del nuovo nodo di inizio
        @param new_goal: tupla contenente le coordinate del nuovo nodo di fine
        '''
        self.mappa.rechargeMappa(new_start, new_goal)

        self.aperta = PriorityQueue()
        self.chiusa = set()
        self.pathToGoal = []

    def printPathToGoal(self):
        '''
        Metodo che stampa il percorso compiuto per andare dalla cella di Start a quella Goal
        '''
        cell = self.mappa.goal
        self.pathToGoal = [cell]
        while cell.parent is not self.mappa.start:
            cell = cell.parent
            self.pathToGoal.append(cell)

        self.pathToGoal = list(reversed(self.pathToGoal))
        '''
        print "Sono in ", (self.mappa.start.x, self.mappa.start.y)
        for cell in self.pathToGoal:
            print "Sono in ", (cell.x, cell.y)
        '''

    def search(self):
        '''
        Ricerca A_star
        '''
        self.aperta.put(self.mappa.start, self.mappa.start.f)

        while not self.aperta.empty():

            f, cell = self.aperta.get()

            self.chiusa.add(cell)
            #print cell.printInfo()

            if cell is self.mappa.goal:
                self.printPathToGoal()
                break

            adjacent_cells = self.mappa.getAdjacentCells(cell)
            for adjacent_cell in adjacent_cells:

                if adjacent_cell.reachable and adjacent_cell not in self.chiusa:

                    if adjacent_cell.g > cell.g:
                        self.mappa.updateCellInfo(cell, adjacent_cell)
                    else:
                        self.mappa.updateCellInfo(cell, adjacent_cell)
                        self.aperta.put(adjacent_cell, adjacent_cell.f)

    
    def percepisciOstacoli(self, comingFrom, datiSensoriali):
        '''
        Metodo per la percezione degli ostacoli limitrofi

        @param comingFrom: tupla contenente l'ultima cella da cui viene il robot

        @returns ostacoli: lista di tuple contenente gli ostacoli percepiti limitrofi
        '''
        (x, y) = (self.mappa.start.x, self.mappa.start.y)
        print "Il robot si trova in posizione ", (x, y)

        def trovaCelleDaPercepire():
            #(x_parent, y_parent) = (self.mappa.start.parent.x, self.mappa.start.parent.y) if self.mappa.start.parent is not None else None
            direzioni = {
                "dietro" : (x+1, y) if x+1 < self.mappa.height else None,
                "davanti" : (x-1, y) if x-1 >= 0 else None,
                "destra" : (x, y+1) if y+1 < self.mappa.width else None,
                "sinistra" : (x, y-1) if y-1 >= 0 else None
            }
            ostacoli = self.mappa.getOstacoli()
            for key in direzioni:
                if direzioni[key] in ostacoli:
                    direzioni[key] = None
                if comingFrom is not None and direzioni[key] is comingFrom:
                    direzioni[key] = None
            return direzioni
        
        direzioni = trovaCelleDaPercepire()
        ostacoli = []
        for key in direzioni:
            if direzioni[key] is not None:
                if datiSensoriali[key]<50 and datiSensoriali[key]>10:
                        print "A " + key + " il sonar misura: ", datiSensoriali[key]
                        ostacoli.append(direzioni[key])
        return ostacoli

