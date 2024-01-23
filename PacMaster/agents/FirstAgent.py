from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.observation import Observation
from Pacman_Complete.constants import *


class FirstAgent(IAgent):
    def __init__(self, gameController):
        super().__init__(gameController)

    def calculateNextMove(self):
        obs = Observation(self.gameController)
        self.takeStats(obs)

        closestMapNode = obs.getClosestMapNode()

        MinDirection = STOP
        minDangerLevel = 99999
        for neighbor in closestMapNode.neighbors:
            dangerLevel = obs.calculateDangerLevel(neighbor.position)

            if dangerLevel < minDangerLevel:
                MinDirection = obs.map.getFromToDirection(closestMapNode, neighbor)
                minDangerLevel = dangerLevel

        return MinDirection
