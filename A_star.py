import heapq

class Cell():
    def __init__(self, x, y, reachable):
        '''
        Inizializzo una nuova cella

        @param x: la coordinata della cella
        @param y: la coordinata della cella
        @param reachable ci dice se la cella e' raggiungibile o meno (e' un ostacolo?)
        '''
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        self.g = 0 #quanto mi costa per arrivare alla cella corrente dalla cella di inizio
        self.h = 0 #quanto mi costa per arrivare alla cella finale da questa cella
        self.f = 0 #funzione di valutazione

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        #print "Putting " + str(item) + " with priority " + str(priority)
        heapq.heappush(self.elements, (priority, item))
        #print "Elements are now: ", self.elements

    def get(self):
        return heapq.heappop(self.elements)

class AStar():

    def __init__(self):
        self.APERTA = PriorityQueue()
        #heapq.heapify(self.APERTA) #mi permette di tenere le celle con funzione di valutazione piu' bassa in testa
        self.CHIUSA = set()
        self.cells = []
        self.grid_height = 10
        self.grid_width = 10

    def init_grid(self, obstacles, (x_start, y_start)):
        '''
        @param obstacles: e' una lista di tuple contenente tutti gli ostacoli nella mappa
        @param (x_start, y_start): e' una tupla che contiene le coordinate della cella da cui parte la ricerca
        '''
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x, y) in obstacles:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(x, y, reachable))
        self.start = self.get_cell(x_start, y_start)
        self.end = self.get_cell(9, 9)

    def get_cell(self, x, y):
        '''
        Restituisce una cella da una lista di celle

        @param x: coordinata x della cella
        @param y: coordinata y della cella
        @returns cell
        '''
        return self.cells[x * self.grid_height + y]

    def get_heuristic(self, cell):
        '''
        Calcola il valore dell'euristica H per una cella: consideriamo la distanza euclidea tra la
        cella corrente e quella finale, e la moltiplichiamo per 10

        @param cell
        @returns valore dell'euristica H
        '''
        return (abs(cell.x - self.end.x) + abs(cell.y - self.end.y))

    def get_adjacent_cells(self, cell):
        '''
        Restituisce le celle adiacenti ad una cella (consideriamo solo movimenti up, down, left, right, no diagonale).
        Il calcolo comincia a partire da dx.

        @oaram cell: cella da cui calcolare le celle adiacenti
        @returns una lista di celle adiacenti
        '''
        cells = []
        if cell.x < self.grid_width - 1:
            cells.append(self.get_cell(cell.x+1, cell.y))
        if cell.y > 0:
            cells.append(self.get_cell(cell.x, cell.y-1))
        if cell.x > 0:
            cells.append(self.get_cell(cell.x-1, cell.y))
        if cell.y<self.grid_height-1:
            cells.append(self.get_cell(cell.x, cell.y+1))
        return cells

    def display_path(self):
        #print "Path: "
        cell = self.end
        self.path = [self.end]
        while cell.parent is not self.start:
            cell = cell.parent
            #print 'cell: %d, %d' %(cell.x, cell.y)
            self.path.append(cell)

    def update_cell(self, adj, cell):
        '''
        Metodo per calcolare G e H per la cella adiacente di una cella (setto il genitore alla cella adiacente)

        @param adj: cella adiacente alla cella corrente
        @param cell: cella corrente da processare
        '''
        adj.g = cell.g + 10
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    def search(self):
        self.APERTA.put(self.start, self.start.f)
        while not self.APERTA.empty():
            # faccio il pop ad APERTA
            f, cell = self.APERTA.get()
            # aggiungo la cella appena presa dalla lista CHIUSA in modo tale da non processarla di nuovo
            self.CHIUSA.add(cell)
            # se la cella appena presa dalla lista e' quella goal, allora termino mostrando il percorso
            if cell is self.end:
                self.display_path()
                break
            # genero le celle adiacenti alla cella corrente
            adj_cells = self.get_adjacent_cells(cell)
            for adj_cell in adj_cells:
                #controllo che la cella non sia un ostacolo o non sia stata gia' espolorata
                if adj_cell.reachable and adj_cell not in self.CHIUSA:
                    #controllo se adj_cell e' in APERTA e se il percorso
                    # corrente e' migliore di quello che c'era precedentemente
                    if adj_cell.g > cell.g:
                        self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        # aggiungo la adj_cell in APERTA
                        self.APERTA.put(adj_cell, adj_cell.f)

def calc_move(cell, next_cell):
    '''
    Ritorna la mossa da compiere per andare da cell a next_cell

    @param cell: e' una tupla contenente le coordinate della cella di partenza
    @param next_cell: e' una tupla contenente le coordinate della cella di arrivo
    @returns move: tupla che contiene la mossa da fare per andare da cell a next_cell
    '''
    return (next_cell[0]-cell[0], next_cell[1]-cell[1])

import random
random.seed(None)

def generate_obstacles(cell):
    '''
    Ritorna una lista di ostacoli, generati casualmente, vicino la cella in cui ci si trovato

    @param cell: e' una tupla contenente le coordinate della cella
    @returns obstacles: lista di ostacoli vicini alla cella
    '''
    obstacles = []
    if cell == (0, 0) or cell == (9, 9):
        return obstacles
    if cell[0] > 0 and cell[0]<9:
        p_x = random.random()
    else:
        p_x = random.random()*random.random()
    if cell[1] > 0 and cell[1]<9:
        p_y = random.random()
    else:
        p_y = random.random()*random.random()
    if p_x*p_y>0.3:
        x_obstacle = random.randint(1, 10)
        if x_obstacle > random.randint(1, 10):
            x_obstacle = cell[0] + 1
            obstacles.append((x_obstacle, cell[1]))
        else:
            x_obstacle = cell[0] - 1
            obstacles.append((x_obstacle, cell[1]))
    if p_x*p_y>0.6:
        y_obstacle = random.randint(1, 10)
        if y_obstacle > random.randint(1, 10):
            y_obstacle = cell[1] + 1
            obstacles.append((cell[0], y_obstacle))
        else:
            x_obstacle = cell[1] - 1
            obstacles.append((cell[0], x_obstacle))
    if (0, 0) in obstacles or (9, 9) in obstacles:
        return []
    print "Gli ostacoli sono: ", obstacles
    return obstacles

def calc_path(start, moves):
    '''
    Stampa il percorso da fare da una cella di partenza, a partire dalle mosse specificate

    @param start: cella di partenza da cui calcolo il percorso
    @param moves: lista di mosse
    '''
    cell = start
    for move in moves:
        next_cell = (cell[0]+move[0], cell[1]+move[1])
        print "Vado da " + str(cell) + " a " + str(next_cell)
        cell = next_cell


start = (0, 0)
moves = []
while True:
    a_star = AStar()
    obstacles = generate_obstacles(start)
    a_star.init_grid(obstacles, start)
    a_star.search()
    if a_star.path == []:
        print "Non ho trovato nessun percorso valido"
        break
    next_cell = (a_star.path[len(a_star.path) - 1].x, a_star.path[len(a_star.path) - 1].y)
    move = calc_move(start, next_cell)
    moves.append(move)
    #print "La mossa per andare da " + str(start) + " a " + str(next_cell) + " e': " + str(move)
    start = next_cell
    if start == (9, 9):
        break

calc_path((0, 0), moves)
