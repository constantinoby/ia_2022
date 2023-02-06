"""
ClauPercepcio:
    POSICIO = 0
    OLOR = 1
    PARETS = 2
"""

import copy
import time

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import ClauPercepcio,AccionsRana,Direccio

from queue import PriorityQueue

class Estat:

    MOVIMENTS = {
        Direccio.BAIX: (0, 1),
        Direccio.DRETA: (1, 0),
        Direccio.DALT: (0, -1),
        Direccio.ESQUERRE: (-1, 0),
    }

    """Inicializamos la clase estat"""
    def __init__(self, info: dict = None, pare=None):

        if info is None:
            info = {}

        self.__info = info
        self.__pare = pare
        self.__nom = "Miquel"
        self.__pes = 0

    """Declaramos el hashing"""
    def __hash__(self):
        return hash(tuple(self.__info))

    """Setter del item"""
    def __setitem__(self, key, value):
        self.__info[key] = value

    """Getter del item"""
    def __getitem__(self, key):
        return self.__info[key]

    def __lt__(self, other):
        return False

    def __eq__(self, other):
        """Overrides the default implementation"""
        return self[ClauPercepcio.POSICIO][self.__nom] == other[ClauPercepcio.POSICIO][self.__nom]

    """Declaramos el metodo genera_fill el cual nos va ha devolver la lista de estados posibles."""
    def genera_fill(self) -> list:
        fills = []

        direccions = [Direccio.DRETA, Direccio.BAIX, Direccio.ESQUERRE, Direccio.DALT]

        """Acciones posibles realizables por la rana"""
        accions = {
            AccionsRana.BOTAR: 2,
            AccionsRana.MOURE: 1
        }

        for accion, saltos in accions.items():
            for direccio in direccions:
                new_pos = self.calcula_casella(
                    posicio=self[ClauPercepcio.POSICIO][self.__nom], dir=direccio, magnitut=saltos)

                """Si la nueva posicion esta fuera del tablero la skipeamos"""
                if new_pos in self[ClauPercepcio.PARETS] or \
                (new_pos[0] > 7 or new_pos[0] < 0) or (new_pos[1] > 7 or new_pos[1] < 0):
                    continue

                """Copiamos el nuevo estado al estado actual, mediante el deepcopy"""
                new_state = copy.deepcopy(self)

                """Si la acción es saltar hacemos esto, si no simplemente nos queremos mover"""
                if AccionsRana.BOTAR == accion:
                    new_state.pare = (self, [(AccionsRana.ESPERAR, direccio),
                                             (AccionsRana.ESPERAR, direccio),
                                             (accion, direccio)])
                    # 6 coste salto + 2*0.5 coste esperar                         
                    new_state.pes = self.__pes + 7
                else:
                    new_state.pare = (self, [(accion, direccio)])
                    new_state.pes = self.__pes + 1

                """Actualizamos la posicion de la rana"""
                new_state[ClauPercepcio.POSICIO][self.__nom] = new_pos

                """Añadimos el nuevo estado a la lista de estados"""
                fills.append(new_state)

        return fills

    def es_meta(self) -> bool:
        return self[ClauPercepcio.POSICIO][self.__nom] == self[ClauPercepcio.OLOR]

    """Calculamos la heuristica mediante la distancia manhattan"""
    def calcula_heuristica(self):
        pos = self[ClauPercepcio.POSICIO][self.__nom]
        pos_pizza = self[ClauPercepcio.OLOR]
        distancia = abs(pos_pizza[0]-pos[0]) + abs(pos_pizza[1]-pos[1])
        return distancia + self.__pes

    @property
    def pare(self):
        return self.__pare

    @pare.setter
    def pare(self, value):
        self.__pare = value
    
    @property
    def pes(self):
        return self.__pes

    @pes.setter
    def pes(self, value):
        self.__pes = value

    @staticmethod
    def calcula_casella(posicio: tuple[int, int], dir: Direccio, magnitut: int = 1):
        mov = Estat.MOVIMENTS[dir]

        return posicio[0] + (mov[0] * magnitut), posicio[1] + (mov[1] * magnitut)

        
class Rana(joc.Rana):
    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(*args, **kwargs)
        self.__oberts = None
        self.__tancats = None
        self.__accions = None

    def pinta(self, display):
        pass

    def cerca(self, estat):

        actual = None
        self.__oberts = PriorityQueue()
        self.__tancats = set()

        self.__oberts.put((estat.calcula_heuristica(), estat))

        """Mientras la lista de abiertos no este vacia"""
        while not self.__oberts.empty():
            _, actual = self.__oberts.get()
            
            """Si el estado ya esta cerrado lo skipeamos"""
            if actual in self.__tancats:
                continue
            
            """Generamos los estados hijos"""
            estats_fills = actual.genera_fill()

            """Si el estado es meta acabamos"""
            if actual.es_meta():
                break

            """Recorremos los estados hijos"""
            for estat_fill in estats_fills:
                self.__oberts.put((estat_fill.calcula_heuristica(), estat_fill))

            """Añadimos el estado a los cerrados"""
            self.__tancats.add(actual)

        if actual.es_meta():
            accions = []
            iterador = actual

            while iterador.pare is not None:
                pare, accio = iterador.pare

                for acc in accio:
                    accions.append(acc)
                iterador = pare
            self.__accions = accions
          

    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        estat_inicial = Estat(percep.to_dict())

        if self.__accions is None:
            start=time.time()
            self.cerca(estat_inicial)
            print("--- %s seconds ---" % (time.time() - start))
            
        if self.__accions:
            acc = self.__accions.pop()
            return acc[0], acc[1]
        else:
            return AccionsRana.ESPERAR