# Robocoosa

PROGETTAZIONE ROBOT

Prendere un oggetto e portarlo in altra posizione
Il robot deve quindi raggiungere la posizione in cui si trova l'oggetto (nota a priori, è le cella (9, 9), determinare l'oggetto e spostarlo
nell'area target associata all'oggetto. Il ciclo di esecuzione è quindi:

while non finiscono gli oggetti:
  - andare a (9, 9);
  - riconoscere l'oggetto (in base al colore);
  - prendere oggetto;
  - spostare l'oggetto nella zona target associata

Possiamo a questo punto scomporre queste singole azioni in 3 macro-azioni:
- muoversi;
- riconosci oggetto;
- prendi oggetto;

Muoversi
L'azione muoversi consiste di tre parti: azioni di base, localizzazione, pianificazione.
Le azioni di base che usiamo sono:
  - avanti();
  - indietro();
  - ruota();
  - fermati();
La fase di localizzazione avviene con i seguenti step:
  - ruota e determina i landmarks;
  - calcola posizione da landmarks;
La fase di pianificazione consiste nell'applicare l'algoritmo A* o D* (da decidere).

Riconosci oggetto
Riconosce un oggetto consiste nell'analizzare un frame, e invocando le seguenti azioni:
  - detectObject();
  - detectArea();

Prendi oggetto
Questa azione permette di poter prendere un oggetto che viene determinato. Gli step da considerare sono:
  - determina posizione oggetto rispetto al robot (determino l'angolo dell'oggetto rispetto al robot);
  - ruota il robot di quell'angolo;
  - avanti() (piano però);
  - cala barra;

Spostare l'oggetto nella zona target associata
Questa funzione è una sorta di Muoversi, ma con posizione target differente.
