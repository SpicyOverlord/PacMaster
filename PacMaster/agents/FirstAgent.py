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

        minDirection = STOP
        minDangerLevel = 99999
        for neighbor in closestMapNode.neighbors:
            if obs.isGhostBetween(closestMapNode.position, neighbor.node.position):
                continue

            dangerLevel = obs.calculateDangerLevel(neighbor.node.position)
            if dangerLevel < minDangerLevel:
                minDirection = neighbor.direction
                minDangerLevel = dangerLevel

        return minDirection
