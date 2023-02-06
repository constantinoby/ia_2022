"""
ClauPercepcio:
    POSICIO = 0
    OLOR = 1
    PARETS = 2
"""
import itertools
import random
from queue import PriorityQueue
import time

from ia_2022 import entorn
from practica1 import joc
from practica1.entorn import AccionsRana, Direccio, ClauPercepcio
from dataclasses import dataclass, field
from typing import Any

class Individuo:

    MOVIMENTS = {
        Direccio.BAIX: (0, 1),
        Direccio.DRETA: (1, 0),
        Direccio.DALT: (0, -1),
        Direccio.ESQUERRE: (-1, 0),
    }

    def __init__(self):
        self.__info = []
        self.__fitness = 0

    def get_info(self):
        return self.__info

    def get_fitness(self):
        return self.__fitness

    def set_info(self, list: list):
        self.__info = list

    # Generador de individuos aleatorios
    def genera_individu(self, genetic_pool: list):
        for i in range(0,10):
            self.__info.append(random.choice(genetic_pool))

    # Mira que el indivudo pasado por parametro se haya generado en un posición segura.
    def es_segur(self, pos_inicial: int, parets: int, mapa: int, meta: int):
        pos_actual = pos_inicial
        value = 0

        for i in self.__info:
            pos_anterior = pos_actual
            if i[0] == AccionsRana.MOURE:
                pos_actual = Individuo.calcula_casella(pos_actual, i[1], 1)
            elif i[0] == AccionsRana.BOTAR:
                pos_actual = Individuo.calcula_casella(pos_actual, i[1], 2)

            value += 1

            # Si pos_actual esta en las paredes o fuera del mapa
            if pos_actual in parets or pos_actual[0] >= mapa[0] or pos_actual[0] < 0 or pos_actual[1] >= mapa[1] or pos_actual[1] < 0:
                if value == 1:
                    return False
                else:
                    self.__info = self.__info[:value - 1]
                    self.__fitness = self.calcular_fitness(pos_anterior, meta)
                    return True

            if pos_actual == meta:
                self.__info = self.__info[:value]
                self.__fitness = len(self.__info) * 0.2
                return True

        self.__fitness = self.calcular_fitness(pos_actual, meta)
        return True

    # Calcula el fitness de un individuo
    def calcular_fitness(self,x,y):
        return abs(y[0]-x[0])+abs(y[1]-x[1])

    # Ver si el individuo llega a la meta
    def es_meta(self, pos_inicial: int, meta: int):
        pos_actual = (pos_inicial[0], pos_inicial[1])
        for accion in self.__info:
            if accion[0] == AccionsRana.MOURE:
                pos_actual = Individuo.calcula_casella(pos_actual, accion[1], 1)
            elif accion[0] == AccionsRana.BOTAR:
                pos_actual = Individuo.calcula_casella(pos_actual, accion[1], 2)

            if pos_actual == meta:
                return True
        return False
    
    @staticmethod
    def calcula_casella(posicio: tuple[int, int], dir: Direccio, magnitut: int = 1):
        mov = Individuo.MOVIMENTS[dir]

        return posicio[0] + (mov[0] * magnitut), posicio[1] + (mov[1] * magnitut)

@dataclass(order=True)
class PrioritizedItem:
    priority: float
    item: Any = field(compare=False)
class Rana(joc.Rana):

    # Decimos el tamaño máximo de la población
    MAX_POBLACIO = 40

    def __init__(self, *args, **kwargs):
        super(Rana, self).__init__(*args, **kwargs)
        self.__accions = None

    def mutacion(self, genetico, generacion, iteracions, percep, fill1_info, fill2_info):

        # Probabilidad del 10% de mutar
        probabilitat = 1 if iteracions > 100 else random.randint(1, 10)
        if probabilitat == 1:
            fill2_info = fill2_info + [random.choice(generacion)]

        fill1 = Individuo()
        fill1.set_info(fill1_info)
        if fill1.es_segur(percep[ClauPercepcio.POSICIO][self.nom], percep[ClauPercepcio.PARETS], percep[ClauPercepcio.MIDA_TAULELL], percep[ClauPercepcio.OLOR]):
            genetico.put(PrioritizedItem(fill1.get_fitness(), fill1))

        fill2 = Individuo()
        fill2.set_info(fill2_info)
        if fill2.es_segur(percep[ClauPercepcio.POSICIO][self.nom], percep[ClauPercepcio.PARETS], percep[ClauPercepcio.MIDA_TAULELL], percep[ClauPercepcio.OLOR]):
            genetico.put(PrioritizedItem(fill2.get_fitness(), fill2))


    def cruce(self, poblacion, genetico, generacion, iteracions, percep):
        
        for i in range(0, self.MAX_POBLACIO - 1, 2):

            ind1 = poblacion[i]
            ind2 = poblacion[i + 1]

            # Seleccionamos un punto de cruce aleatorio
            cross_index = min(len(ind1.get_info()), len(ind2.get_info())) - 1
            cross_index = random.randint(0, cross_index)

            # Cruzamos los individuos
            fill1_info = ind1.get_info()[:cross_index] + ind2.get_info()[cross_index:]
            fill2_info = ind2.get_info()[:cross_index] + ind1.get_info()[cross_index:]

            self.mutacion(genetico, generacion, iteracions, percep, fill1_info, fill2_info)



    def genetic(self, percep: entorn.Percepcio):
        
        direccions = [Direccio.DRETA, Direccio.BAIX, Direccio.ESQUERRE, Direccio.DALT]
        accions = [AccionsRana.BOTAR, AccionsRana.MOURE, AccionsRana.ESPERAR]
        # Array de generaciones
        generacion = []

        # Generamos todos los estados posibles 
        for state in itertools.product(accions, direccions):
            generacion.append(state)


        poblacion = []
        # Generamos todos los invividuos posibles y los metemos en la poblacion
        while len(poblacion) < self.MAX_POBLACIO:
            individuo = Individuo()
            individuo.genera_individu(generacion)
            if individuo.es_segur(percep[ClauPercepcio.POSICIO][self.nom], percep[ClauPercepcio.PARETS],percep[ClauPercepcio.MIDA_TAULELL], percep[ClauPercepcio.OLOR]):
                poblacion.append(individuo)

        # Bucle de seleccion de individuos
        end = False
        ind_sol = None
        n = 0
        while not end:
            genetico = PriorityQueue()
            # Recorremos la poblacion
            for individuo in poblacion:
                # Comprovar si es solució
                if individuo.es_meta(percep[ClauPercepcio.POSICIO][self.nom], percep[ClauPercepcio.OLOR]):
                    end = True
                    ind_sol = individuo
                    break
            
                # Si no es solucion, metemos el individuo en la cola y lo ordenamos por fitness
                genetico.put(PrioritizedItem(individuo.get_fitness(), individuo))

            # Cruzamos los individuos
            self.cruce(poblacion, genetico, generacion, n, percep)

            # Si no es solucion, recorremos la cola y actualizamos la poblacion
            if not end:
                poblacion = []
                for i in range(self.MAX_POBLACIO):
                    ind = genetico.get()
                    ind = ind.item
                    poblacion.append(ind)

            n += 1

        # Recorremos las acciones guardadas en el individuo solucion
        accions = []
        for i in ind_sol.get_info():
            accions.insert(0, i)
            if i[0] == AccionsRana.BOTAR:
                accions.insert(0, (AccionsRana.ESPERAR, Direccio.DRETA))
                accions.insert(0, (AccionsRana.ESPERAR, Direccio.DRETA))

        self.__accions = accions
        return True

    def actua(self, percep: entorn.Percepcio) -> entorn.Accio | tuple[entorn.Accio, object]:

        if self.__accions is None:
            start = time.time()
            self.genetic(percep)
            print("--- %s seconds ---" % (time.time() - start))

        if len(self.__accions) > 0:
            acc = self.__accions.pop()

            return acc[0], acc[1]
        else:
            return AccionsRana.ESPERAR
