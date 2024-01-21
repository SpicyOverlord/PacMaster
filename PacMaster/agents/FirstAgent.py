from PacMaster.agents.Iagent import IAgent
from PacMaster.observation import Observation
from Pacman_Complete.constants import *


class FirstAgent(IAgent):
    def __init__(self, gameController):
        super().__init__(gameController)

    def calculateNextMove(self):
        obs = Observation(self.gameController)

        print("CALCULATING NEXT MOVE (not implemented...)")
        print(obs.getPacmanPosition())
        return STOP
