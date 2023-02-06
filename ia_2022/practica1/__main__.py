import sys

sys.path.append('C:\\Users\\csbye\\OneDrive\\Escritorio\\ia_2022')

from practica1 import agent_amplada,agent_heuristica,agent_minimax,agent_genetic, joc

def main():
    
    #Para usar amplada  o heurisitica se descomenta esta parte

    rana = agent_amplada.Rana("Miquel")
    # rana = agent_heuristica.Rana("Miquel")
    # lab = joc.Laberint([rana], parets=True)

    #Para usar minimax se descomenta esta parte
    # rana = agent_minimax.Rana("Miquel")
    # rana2 = agent_minimax.Rana("Juan")
    # lab = joc.Laberint([rana, rana2], parets=True)

    #Para usar genetic se descomenta esta parte
    rana = agent_genetic.Rana("Miquel")
    lab = joc.Laberint([rana], parets=True)

    lab.comencar()


if __name__ == "__main__":
    main()
