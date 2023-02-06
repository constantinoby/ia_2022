import copy
import time

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import AccionsRana, Direccio, ClauPercepcio


class Estat:
    MOVIMENTS = {
        Direccio.BAIX: (0, 1),
        Direccio.DRETA: (1, 0),
        Direccio.DALT: (0, -1),
        Direccio.ESQUERRE: (-1, 0),
    }

    def __init__(self, nom_agent: str, info: dict = None, pare=None):
        if info is None:
            info = {}

        self.__info = info
        self.__pare = pare

        self.__dir_bot = None
        self.__bots_restants = 0
        self.__nom = nom_agent

    def __hash__(self):
        return hash(tuple(self.__info))

    def __getitem__(self, key):
        return self.__info[key]

    def __setitem__(self, key, value):
        self.__info[key] = value

    def __eq__(self, other):
        if self.__pare and other.pare:
            return self.__info == other.__info and self.__pare[1] == other.pare[1]
        else:
            return self.__info == other.__info and self.__bots_restants == other.__bots_restants

    def es_meta(self) -> bool:
        return self[ClauPercepcio.POSICIO][self.__nom] == self[ClauPercepcio.OLOR]

    def iniciar_bot(self, direccio: Direccio):
        self.__dir_bot = direccio
        self.__bots_restants = 2

    def seguir_bot(self):
        self.__bots_restants -= 1
        return self.__dir_bot

    def botant(self) -> bool:
        return self.__bots_restants > 0

    def genera_fill(self) -> list:
        if self.botant():
            direccio = self.seguir_bot()
            # Si ha acabado el salto, podemos poner la posicion final
            if not self.botant():
                new_state = copy.deepcopy(self)
                new_state.pare = ( self, (AccionsRana.ESPERAR, Direccio.ESQUERRE))
                new_pos = self.calcula_casella(posicio=self[ClauPercepcio.POSICIO][self.__nom], dir=direccio, magnitut=2)
                new_state[ClauPercepcio.POSICIO][self.__nom] = new_pos
                return [new_state]
            else:
                new_state = copy.deepcopy(self)
                new_state.pare = (self, (AccionsRana.ESPERAR, Direccio.DALT))
                return [new_state]

        fills = []
        direccions = [Direccio.DRETA, Direccio.BAIX, Direccio.ESQUERRE, Direccio.DALT]

        # Caso moverse
        for direccio in direccions:
            new_pos = self.calcula_casella(posicio=self[ClauPercepcio.POSICIO][self.__nom], dir=direccio, magnitut=1)

            if new_pos in self[ClauPercepcio.PARETS] or (new_pos[0] > 7 or new_pos[0] < 0) or (new_pos[1] > 7 or new_pos[1] < 0):
                continue

            new_state = copy.deepcopy(self)
            new_state.pare = (self, (AccionsRana.MOURE, direccio))
            new_state[ClauPercepcio.POSICIO][self.__nom] = new_pos
            fills.append(new_state)

        # Caso salto
        for direccio in direccions:
            new_pos = self.calcula_casella(posicio=self[ClauPercepcio.POSICIO][self.__nom], dir=direccio, magnitut=2)

            if new_pos in self[ClauPercepcio.PARETS] or (new_pos[0] > 7 or new_pos[0] < 0) or (new_pos[1] > 7 or new_pos[1] < 0):
                continue

            new_state = copy.deepcopy(self)
            new_state.iniciar_bot(direccio)
            new_state.pare = (self, (AccionsRana.BOTAR, direccio))
            fills.append(new_state)

        # Esperar
        new_state = copy.deepcopy(self)
        new_state.pare = (self, (AccionsRana.ESPERAR, Direccio.BAIX))
        fills.append(new_state)

        return fills

    @property
    def pare(self):
        return self.__pare

    @pare.setter
    def pare(self, value):
        self.__pare = value

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

    def cerca(self, estat):
        self.__oberts = []
        self.__tancats = set()

        self.__oberts.append(estat)

        actual = None
        while len(self.__oberts) > 0:
            actual = self.__oberts[0]
            self.__oberts = self.__oberts[1:]
            if actual in self.__tancats:
                continue

            estats_fills = actual.genera_fill()

            if actual.es_meta():
                break

            for estat_fill in estats_fills:
                self.__oberts.append(estat_fill)

            self.__tancats.add(actual)

        if actual.es_meta():
            accions = []
            iterador = actual

            while iterador.pare is not None:
                pare, accio = iterador.pare
                accions.append(accio)
                iterador = pare
            self.__accions = accions
            return True
        else:
            return False

    def actua(
            self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        estat_inicial = Estat(self.nom, percep.to_dict())
        if self.__accions is None:
            start = time.time()
            self.cerca(estat_inicial)
            print("--- %s seconds ---" % (time.time() - start))

        if len(self.__accions) > 0:
            acc = self.__accions.pop()
            return acc[0], acc[1]
        else:
            return AccionsRana.ESPERAR
