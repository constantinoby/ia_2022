"""
ClauPercepcio:
    POSICIO = 0
    OLOR = 1
    PARETS = 2
"""
import copy
from dataclasses import dataclass

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import AccionsRana, Direccio, ClauPercepcio


class Estat:
    MAX_PROFUNDITAT = 4

    MOVIMENTS = {
        Direccio.BAIX: (0, 1),
        Direccio.DRETA: (1, 0),
        Direccio.DALT: (0, -1),
        Direccio.ESQUERRE: (-1, 0),
    }

    def __init__(self, nom_max: str, nom_min: str, info: dict = None, pare=None):
        if info is None:
            info = {}

        self.__info = info
        self.__pare = pare

        self.__nom_max = nom_max
        self.__nom_min = nom_min

    def __hash__(self):
        return hash(tuple(self.__info))

    def __getitem__(self, key):
        return self.__info[key]

    def __setitem__(self, key, value):
        self.__info[key] = value

    def __eq__(self, other):
        return self.__info == other.__info

    def nom_altre(self, nom: str) -> str:
        if nom == self.__nom_max:
            return self.__nom_min
        return self.__nom_max

    # Calcula la distancia Manhattan entre el agente y la pizza
    def calcula_heurisitica(self, nom: str) -> int:
        pos = self[ClauPercepcio.POSICIO][nom]
        pizza = self[ClauPercepcio.OLOR]
        return abs(pizza[0] - pos[0]) + abs(pizza[1] - pos[1])

    # Vemos que rana esta mas cerca de la pizza
    def evaluar(self, nom: str, es_max: bool, profunditat: int):
        if self.es_meta(nom) or profunditat == self.MAX_PROFUNDITAT:
            distancia_altre = self.calcula_heurisitica(self.nom_altre(nom))
            distancia_rana = self.calcula_heurisitica(nom)

            if es_max:
                return distancia_altre - distancia_rana
            else:
                return distancia_rana - distancia_altre

        return None

    # Miramos si alguna rana a llegado a la pizza
    def es_meta(self, nom: str) -> bool:
        return self[ClauPercepcio.POSICIO][nom] == self[ClauPercepcio.OLOR] or \
               self[ClauPercepcio.POSICIO][self.nom_altre(nom)] == self[ClauPercepcio.OLOR]

    # Generamos los hijos de cada nodo
    def genera_fill(self, nom: str) -> list:
        fills = []

        direccions = [Direccio.DRETA, Direccio.BAIX, Direccio.ESQUERRE, Direccio.DALT]

        # Caso mover
        for direccio in direccions:
            new_pos = self.calcula_casella(posicio=self[ClauPercepcio.POSICIO][nom], dir=direccio, magnitut=1)

            # Verificamos que la casilla no este ocupada por una pared o que este fuera del tablero
            if new_pos in self[ClauPercepcio.PARETS] or (new_pos[0] > 7 or new_pos[0] < 0) or (new_pos[1] > 7 or new_pos[1] < 0):
                continue

            # En caso de que todo correcto creamos el nuevo estado
            new_state = copy.deepcopy(self)
            new_state.pare = (self, (AccionsRana.MOURE, direccio))
            new_state[ClauPercepcio.POSICIO][nom] = new_pos
            fills.append(new_state)

        # Caso salto
        for direccio in direccions:
            new_pos = self.calcula_casella(
                posicio=self[ClauPercepcio.POSICIO][nom], dir=direccio, magnitut=2)

            # Verificamos que la casilla no este ocupada por una pared o que este fuera del tablero
            if new_pos in self[ClauPercepcio.PARETS] or \
                    (new_pos[0] > 7 or new_pos[0] < 0) or (new_pos[1] > 7 or new_pos[1] < 0):
                continue

            # En caso de que todo correcto creamos el nuevo estado
            new_state = copy.deepcopy(self)
            new_state.pare = (self, (AccionsRana.BOTAR, direccio))
            new_state[ClauPercepcio.POSICIO][nom] = new_pos
            fills.append(new_state)

        # Como ultima opción tenemos que la rana espere
        new_state = copy.deepcopy(self)
        new_state.pare = (self, (AccionsRana.ESPERAR, Direccio.DRETA))
        fills.append(new_state)

        return fills

    @property
    def pare(self):
        return self.__pare

    @pare.setter
    def pare(self, value):
        self.__pare = value

    # Calculamos la casilla a la que se movera la rana
    @staticmethod
    def calcula_casella(posicio: tuple[int, int], dir: Direccio, magnitut: int = 1):
        mov = Estat.MOVIMENTS[dir]

        return posicio[0] + (mov[0] * magnitut), posicio[1] + (mov[1] * magnitut)
@dataclass
class Puntuacion:
    puntuacio: int
    estat: Estat
    def __gt__(self, other): return self.puntuacio > other.puntuacio
    def __lt__(self, other): return self.puntuacio < other.puntuacio
class Rana(joc.Rana):
    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(args[0])
        self.__accions = []

        self.__es_max = None
        self.__nom_altre = None

    
    # Metodo que mira los movimiento que se pueden hacer por parte de min y max
    def minimax(self, estat: Estat, profunditat: int, es_max: bool, nom: str) -> Puntuacion:
        # Calculamos el score de la rana que nos llega  por parametro
        score = estat.evaluar(nom, es_max, profunditat)
        if score is not None:
            iterador = estat
            while iterador.pare is not None and iterador.pare[0].pare is not None:
                pare, accio = iterador.pare
                iterador = pare

            return Puntuacion(score, copy.deepcopy(iterador))

        # Genero la puntuacion de todos los hijos que han sido creado en genera_fill
        puntuacio_fills = [self.minimax(estat_fill, profunditat + 1, not es_max, estat.nom_altre(nom)) for estat_fill in estat.genera_fill(nom)]

        # Devolvemos el movimiento correspondiente a max o min
        if es_max:
            return max(puntuacio_fills)
        else:
            return min(puntuacio_fills)

        
    # Miramos que accion se va a realizar
    def cerca(self, estat_inicial: Estat):
        # Buscamos la accion a realizar
        resultat = self.minimax(estat_inicial, 0, self.__es_max, self.nom)

        if resultat.estat.pare is not None:
            accio_final = resultat.estat.pare[1]
        else:
            accio_final = (AccionsRana.ESPERAR, Direccio.BAIX)

        if accio_final[0] == AccionsRana.BOTAR:
            self.__accions.append((AccionsRana.ESPERAR, Direccio.ESQUERRE))
            self.__accions.append((AccionsRana.ESPERAR, Direccio.ESQUERRE))
        self.__accions.append(accio_final)

    def nombres(self, percep: entorn.Percepcio):
        noms_agents = list(percep[ClauPercepcio.POSICIO].keys())
        #Miramos si somos la rana max o min
        if self.nom == noms_agents[0]:
            self.__es_max = True
            self.__nom_altre = noms_agents[1]
        else:
            self.__es_max = False
            self.__nom_altre = noms_agents[0]

    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        #Obtenemos los nombres, la primera rana sera asignada como max y la segunda como min
        self.nombres(percep)

        # Asignamos el estado inicial de la rana max o min
        if self.__es_max:
            estat_inicial = Estat(self.nom, self.__nom_altre, percep.to_dict())
        else:
            estat_inicial = Estat(self.__nom_altre, self.nom, percep.to_dict())

        if len(self.__accions) == 0:
            self.cerca(estat_inicial)

        if len(self.__accions) > 0:
            accio, direccio = self.__accions.pop()
            return accio, direccio
        else:
            return AccionsRana.ESPERAR