import random

import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacMaster.Genetic.WeightContainer import WeightContainer
from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.map import MapNode
from PacMaster.utils.observation import Observation
from PacMaster.utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class CollectorAgent(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController)

    def calculateNextMove(self):
        obs = Observation(self.gameController)
        self.takeStats(obs)

        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT

        # DebugHelper.drawMap(obs)
        # DebugHelper.drawPelletLevels(obs)

        pacmanPosition = obs.getPacmanPosition()
        mapPos = obs.map.createMapPosition(pacmanPosition)
        if mapPos.isBetweenMapNodes:
            return STOP
        return self.__getMaxPelletDirectionFromCustomNode__(obs)

    def __getDirection__(self, obs: Observation, target: Vector2) -> int:
        pacmanPosition = obs.getPacmanPosition()
        if pacmanPosition.y == target.y:
            if pacmanPosition.x < target.x:
                return RIGHT
            else:
                return LEFT
        else:
            if pacmanPosition.y < target.y:
                return DOWN
            else:
                return UP

    def __getMaxPelletDirectionFromCustomNode__(self, obs: Observation) -> int:
        startMapNode, startIsCustom = obs.map.getOrCreateCustomMapNodeOnVector(obs.getPacmanPosition())

        maxPelletLevel = 0
        maxPelletDirection = STOP
        for neighborContainer in startMapNode.neighborContainers:
            endMapNode, path, distance = obs.map.getPathToEndOfDangerZoneInDirection(startMapNode,
                                                                                     neighborContainer.direction)

            pelletsInPath = obs.getPelletCountInPath(path)

            pathPelletLevel = obs.calculatePelletLevel(endMapNode.position) * (pelletsInPath + 1)
            if pathPelletLevel > maxPelletLevel:
                maxPelletLevel = pathPelletLevel
                maxPelletDirection = neighborContainer.direction

        if maxPelletLevel <= 1:
            nearestPelletPosition = obs.getNearestPelletPosition()
            nearestPelletMapNode = obs.map.getNearestMapNode(nearestPelletPosition, snapToGrid=False)
            pelletPath, _ = obs.map.calculateShortestPath(startMapNode.position, nearestPelletMapNode.position)

            maxPelletDirection = self.__getDirection__(obs, pelletPath[1])

        return maxPelletDirection
