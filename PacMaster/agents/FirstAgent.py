import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacMaster.agents.Iagent import IAgent
from PacMaster.observation import Observation
from Pacman_Complete.constants import *


class FirstAgent(IAgent):
    def __init__(self, gameController):
        super().__init__(gameController)

    def calculateNextMove(self):
        obs = Observation(self.gameController)
        self.takeStats(obs)

        closestNodePosition = obs.getClosestNodePosition()
        closestGhostPosition = obs.getClosestGhostPosition()
        closestNode = obs.getNode(closestNodePosition)

        minDirection = RIGHT
        minDistance = 0
        for direction in [RIGHT, LEFT, UP, DOWN]:
            if closestNode.neighbors[direction] is not None:
                distance = obs.manhattenDistance(closestNode.neighbors[direction].position, closestGhostPosition)

                if distance > minDistance:
                    minDirection = direction
                    minDistance = distance

        return minDirection
