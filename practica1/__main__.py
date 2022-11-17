import sys

sys.path.append('C:\\Users\\csbye\\OneDrive\\Escritorio\\IA\\Github\\ia_2022')

from practica1 import agent_amplada,agent_heuristica,agent_minimax, joc


def main():
    #rana = agent_amplada.Rana("Miquel")
    rana = agent_heuristica.Rana("Miquel")
    lab = joc.Laberint([rana], parets=True)

    #rana = agent_minimax.Rana("Papafritta", es_max=True)
    #rana2 = agent_minimax.Rana("Billy", es_max=False)
    #lab = joc.Laberint([rana, rana2], parets=True)
    lab.comencar()


if __name__ == "__main__":
    main()
