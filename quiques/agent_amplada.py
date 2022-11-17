from ia_2022 import entorn
from quiques.agent import Barca, Estat, Lloc
from quiques.entorn import AccionsBarca, ClauPercepcio


class BarcaAmplada(Barca):
    def __init__(self):
        super(BarcaAmplada, self).__init__()
        self.__oberts = None
        self.__tancats = None
        self.__accions = None

    def actua(self, percep: entorn.Percepcio) -> entorn.Accio | tuple[entorn.Accio, object]:

        """Estado inicial"""
        if self.__oberts is None:
            self.__oberts = [Estat({ClauPercepcio.LLOC: Lloc.Esquerra})]
            self.__tancats = set()
            self.__accions = []
            
        """Si no hay Oberts, paramos el barco"""
        if len(self.__oberts) == 0:
            return AccionsBarca.ATURA
        
        """Asignamos el Obert que sacamos de la pila y lo metemos a los tancats"""
        estat_actual = self.__oberts.pop()
        self.__tancats.add(estat_actual)


        if estat_actual[ClauPercepcio.LLOC] == Lloc.Dreta:
            return AccionsBarca.ATURA
        
        for accio in Estat.acc_poss:
            estat_nou = self.__aplica_accio(estat_actual, accio)
            if estat_nou not in self.__tancats:
                self.__oberts.append(estat_nou)
                self.__accions.append(accio)
            
        return AccionsBarca.MOURE, self.__accions.pop()
        pass
