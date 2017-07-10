
class Cell():
    '''
    Attributi
        reachable(Boolean): booelano che indica la raggiungibilita' della cella;
        x (Int): e' la coordinata x della cella;
        y (Int): e' la coordinata y della cella;
        parent (Cell): e' la cella (Cell() object) genitore di questa cella;
        g (Double): indica quanto costa arrivare alla cella corrente dalla cella di inizio
        h (Double): indica quanto costa arrivare alla cella finale dalla cella corrente
        f (Double): funzione di valutazione della ricerca (f+g), ovvero quanto costa arrivare
                    alla cella finale con un percorso che passa dalla cella corrente
    '''
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
        self.g = 0
        self.h = 0
        self.f = 0

    def printInfo(self):
        print "Sono la cella di coordinate: ", (self.x, self.y)
        if self.parent is not None:
            print "La mia cella genitore nel percorso e' ", (self.parent.x, self.parent.y)
        print "Le mie funzioni valgono (g, h, f) = ", (self.g, self.h, self.f)
