""" Mòdul que conté l'agent per jugar al joc de les monedes.

Percepcions:
    ClauPercepcio.MONEDES
Solució:
    " XXXC"

Definir el estado, busqueda con cola de prioridad  y heurisitica 

Hacer clase estado y dentro metodo heurisitca
"""

from ia_2022 import agent, entorn
from monedes.entorn import ClauPercepcio

SOLUCIO = " XXXC"


class AgentMoneda(agent.Agent):
    def __init__(self):
        super().__init__(long_memoria=0)
        self.__oberts = None
        self.__tancats = None
        self.__accions = None

    def pinta(self, display):
        print(self._posicio_pintar)

    def estado(self) -> object:
        self._estadoActual = ClauPercepcio.MONEDES
        heuristica = self.heuristica(self._estadoActual)
        pass

    """ 
    Calculamos heuristica del estado 
    """
    def heuristica(self, estado) -> int:

        pass
    
    def generahijos(self, estado):

        pass

    

    def actua(
        self, percep: entorn.Percepcio
    ) -> entorn.Accio | tuple[entorn.Accio, object]:
        pass
