from __future__ import print_function
from cell import Cell

class Mappa():
    '''
    Attributi
        width (Int): contiene la larghezza della mappa;
        height (Int): contiene l'altezza della mappa;
        start (Cell): corrisponde al punto di inizio della mappa, e' un oggetto Cell;
        goal (Cell): corrisponde al punto di goal della mappa, e' un oggetto Cell;
        cells ([Cell]): e' una lista di Cell() objects che contiene le informazioni sulle celle della mappa;
    '''

    def __init__(self, width=0, height=10, start=(0, 0), goal=(9,9)):

        self.width = width
        self.height = height
        self.start = Cell(start[0], start[1], True)
        self.goal = Cell(goal[0], goal[1], True)
        self.cells = []
        # inizializzo le celle tutte libere
        self.initCells()

    def initCells(self, obstacles=[], start=(0, 0), goal=(9, 9)):
        '''
        Metodo che inizializza le celle della mappa (le setta tutte raggiungibili)
        '''
        self.cells = []
        for x in range(self.height):
            for y in range(self.width):
                if (x, y) in obstacles:
                    reachable = False
                else:
                    reachable = True
                new_cell = Cell(x, y, reachable)
                self.cells.append(new_cell)

        self.start = self.getCell(start[0], start[1])
        self.goal = self.getCell(goal[0], goal[1])

    def setOstacoli(self, ostacoli):
        '''
        Metodo che aggiorna le celle passate come parametro come non raggiungibili

        @param ostacoli: e' una lista di tuple, [(x, y)], contenente le celle da aggiornare
        '''

        for (x, y) in ostacoli:
            for cell in self.cells:
                if (cell.x, cell.y) == (x, y):
                    cell.reachable = False

    def printMappa(self, pathToGoal=[]):
        '''
        Metodo che stampa la mappa come una griglia
        '''

        for x in range(self.height):
            print("[ ", end='')
            for y in range(self.width):
                if (x, y) in pathToGoal or self.getCell(x, y) == self.start:
                    print("r ", end='')
                elif self.getCell(x, y).reachable is True:
                    print("0 ", end='')
                else:
                    print("x ", end='')
            print("] ", end='\n')

    def getCell(self, x, y):
        '''
        Metodo che restituisce una cella (Cell object) date le coordinate in input

        @param x: coordinata x della cella
        @param y: coordinata y della cella
        @returns cell: e' un oggetto Cell()
        '''
        return self.cells[x * self.height + y]

    def getOstacoli(self):
        '''
        Metodo che restituisce gli ostacoli presenti nella mappa

        @returns ostacoli: e' una lista di tuple contenenti le coordinate degli ostacoli
        '''
        ostacoli = []
        for cell in self.cells:
            if cell.reachable is False:
                ostacoli.append((cell.x, cell.y))
        return ostacoli

    def getHeuristic(self, cell):
        '''
        Calcola il valore dell'euristica H per una cella: consideriamo la distanza euclidea tra la
        cella corrente e quella finale, e la moltiplichiamo per 10

        @param cell: e' un oggetto Cell()
        @returns valore dell'euristica H
        '''
        return (abs(cell.x - self.goal.x) + abs(cell.y - self.goal.y))

        from scipy.spatial import distance
        return distance.euclidean((cell.x, cell.y), (self.goal.x, self.goal.y))*10

    def updateCellInfo(self, cell, adjacent):
        '''
        Metodo per calcolare G e H per la cella adiacente di una cella (setto il genitore alla cella adiacente)

        @param adjacent: cella adiacente alla cella corrente, Cell object
        @param cell: cella corrente da processare, Cell object
        '''

        adjacent.g = cell.g + 10
        adjacent.h = self.getHeuristic(adjacent)
        adjacent.f = adjacent.h + adjacent.g
        adjacent.parent = cell

    def getAdjacentCells(self, cell):
        '''
        Restituisce le celle adiacenti ad una cella (consideriamo solo movimenti up, down, left, right, no diagonale).
        Il calcolo comincia a partire da dx.

        @oaram cell: cella da cui calcolare le celle adiacenti, Cell object
        @returns una lista di celle adiacenti
        '''
        cells = []
        if cell.x < self.width - 1:
            cells.append(self.getCell(cell.x+1, cell.y))
        if cell.y > 0:
            cells.append(self.getCell(cell.x, cell.y-1))
        if cell.x > 0:
            cells.append(self.getCell(cell.x-1, cell.y))
        if cell.y<self.height-1:
            cells.append(self.getCell(cell.x, cell.y+1))
        return cells

    def rechargeMappa(self, newStart, newGoal):
        '''
        Metodo che aggiorna la mappa in base al rilevamento di ostacoli, al setting di un nuovo punto di start, e di un nuovo goal

        @param ostacoli: e' una lista di tuple, [(x, y)], contenente le celle da aggiornare
        @param newStart: e' una tupla contenente la coordinata del nuovo start
        @param newGoal: e' una tupla contenente la coordinata del nuovo goal
        '''
        for cell in self.cells:
            if cell.reachable is True:
                cell.g = 0
                cell.h = 0
                cell.f = 0

        self.start = self.getCell(newStart[0], newStart[1])
        if newGoal is not None:
            self.goal = self.getCell(newGoal[0], newGoal[1])

    def printMappaAndCellsInfo(self):
        print("\n")
        print("\nLa cella di start e': ")
        self.start.printInfo()
        print("start == (1, 0)", self.start is self.getCell(1, 0))
        print("\n")
        print("\nLa cella di arrivo e': ")
        self.goal.printInfo()
        print("\nStampo le informazioni di tutte le celle della mappa")
        for cell in self.cells:
            print(cell.printInfo())
