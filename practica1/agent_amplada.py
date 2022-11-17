"""
ClauPercepcio:
    POSICIO = 0
    OLOR = 1
    PARETS = 2
"""
import copy

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import ClauPercepcio,AccionsRana,Direccio

class Estat:

    """Inicializamos la clase estat"""
    def __init__(self, info: dict= None, pare= None  ):

        if info is None:
            info = {}

        self.__info = info
        self.__pare = pare
        self.__nom= "Miquel"
        
    """Declaramos el hashing"""
    def __hash__(self):
        return hash(self.__info[ClauPercepcio.POSICIO][self.__nom])

    """Setter del item"""
    def __setitem__(self, key, value):
        self.__info[key] = value

    """Getter del item"""
    def __getitem__(self, key):
        return self.__info[key]

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
                new_pos=joc.Laberint._calcula_casella(posicio=self[ClauPercepcio.POSICIO][self.__nom], dir=direccio, magnitut=saltos)
                
                """Si la nueva posicion esta fuera del tablero la skipeamos"""
                if new_pos in self[ClauPercepcio.PARETS] or \
                (new_pos[0] > 7 or new_pos[0] < 0) or (new_pos[1] > 7 or new_pos[1] < 0):
                    continue
                
                """Copiamos el nuevo estado al estado actual, mediante el deepcopy"""
                new_state= copy.deepcopy(self)

                """Si la acción es saltar hacemos esto, si no simplemente nos queremos mover"""
                if AccionsRana.BOTAR == accion:
                    new_state.pare=(self, [(AccionsRana.ESPERAR, direccio), 
                                           (AccionsRana.ESPERAR, direccio),
                                           (accion,direccio)])
                else:
                    new_state.pare=(self, [(accion,direccio)])
            
                """Actualizamos la posicion de la rana"""
                new_state[ClauPercepcio.POSICIO][self.__nom]= new_pos

                """Añadimos el nuevo estado a la lista de estados"""
                fills.append(new_state)
        
        return fills

    def es_meta(self) -> bool:
        return self[ClauPercepcio.POSICIO][self.__nom] == self[ClauPercepcio.OLOR]

    @property
    def pare(self):
        return self.__pare

    @pare.setter
    def pare(self, value):
        self.__pare = value


class Rana(joc.Rana):
    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(*args, **kwargs)
        self.__oberts = None
        self.__tancats = None
        self.__accions = None

    def pinta(self, display):
        pass

    def _cerca(self, estat):

        actual = None

        self.__oberts = []
        self.__tancats = set()

        self.__oberts.append(estat)

        """Mientras haya estados abiertos"""
        while len(self.__oberts) > 0:
            actual=self.__oberts[0]
            self.__oberts = self.__oberts[1:]
            """Si el estado ya esta cerrado lo skipeamos"""
            if actual in self.__tancats:
                continue

            """Generamos los estados hijos"""
            estats_fills =actual.genera_fill()

            """Si el estado es meta acabamos"""
            if actual.es_meta():
                break

            for estat_fill in estats_fills:
                self.__oberts.append(estat_fill)

            """Añadimos el estado a los cerrados"""
            self.__tancats.add(actual)

    
        if actual.es_meta():
            accions=[]
            iterador=actual

            while iterador.pare is not None:
                pare, accions_pare=iterador.pare

                for accio in accions_pare:
                    accions.append(accio)
                iterador=pare
            self.__accions=accions
            return True
        else:
            return False

    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        estat_inicial = Estat(percep.to_dict())

        if self.__accions is None:
            self._cerca(estat_inicial)
        
        if self.__accions:
            accio= self.__accions.pop()
            return accio[0], accio[1]
        else:
            return AccionsRana.ESPERAR


"""
    def minimax(estat, torn_de_max):
        score=estat.evaluar()
        if score:
            return score
        
        puntuacio_fills=[minimax(estat_fill, not torn_de_max) for estat_fill in estat.genera_fill()]
        if torn_de_max:
            return max(puntuacio_fills)
        else:
            return min(puntuacio_fills)
    

    def evaluar(estat):
        if estat.es_meta():
            return puntuacion

    
    La puntuacion una para los dos jugadores, misma puntuacion en turno max y min, siempre misma cerca, funcion que tenga la puntuacion conjunta.

    El max que sea mayor significa que el min esta mas lejos, 
    cogemos la posicion de max y min y la posicion de la pizza y miramos quien esta mas cerca de la pizza, 
    el que este mas cerca es el que tiene mas puntuacion.


    Algoritmo generico, cogemos los X hijos de la rana y miramos todos los caminos posibles hasta la pizza, quien sea mejor ese elegimos.

    Como minimax limitamos profundidad y miramos el camino que mejor nos lleva a la pizza. 
"""