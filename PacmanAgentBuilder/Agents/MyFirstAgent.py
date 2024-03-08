import random

import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacmanAgentBuilder.Genetics.WeightModifier import WeightModifier
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Iagent import IAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.Map import MapNode
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class MyFirstAgent(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        return WeightContainer({
            'fleeThreshold': 0.117,
            'pelletLevelDistance': 32.945,
            'wayTooCloseThreshold': 89.816,
            'tooCloseThreshold': 166.13,
            'tooFarAwayThreshold': 1167.553,
            'wayTooCloseValue': 375.088,
            'tooCloseValue': 67.789, 'dangerZoneMultiplier': 1.424,
            'dangerZoneMiddleMapNodeMultiplier': 1.26,
            'ghostInDangerZoneMultiplier': 1.413,
            'closestGhostMultiplier': 1.047,
            'ghostIsCloserMultiplier': 1.728,
            'edgeMultiplier': 1.378
        })

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        return WeightContainer({
            'fleeThreshold': 0.2,
            'pelletLevelDistance': 60,
            'wayTooCloseThreshold': 100,
            'tooCloseThreshold': 300,
            'tooFarAwayThreshold': 800,
            'wayTooCloseValue': 300,
            'tooCloseValue': 100,
            'dangerZoneMultiplier': 1,
            'dangerZoneMiddleMapNodeMultiplier': 1,
            'ghostInDangerZoneMultiplier': 1,
            'closestGhostMultiplier': 1,
            'ghostIsCloserMultiplier': 1,
            'edgeMultiplier': 1}
        )

    def calculateNextMove(self, obs: Observation):

        if self.__isInDanger__(obs):
            return self.__flee__(obs)

        elif self.__isOnNode__(obs):
            return self.__collect_(obs)

        # don't change direction
        return STOP

    def __getDirection__(self, obs: Observation, vector: Vector2) -> int:
        pacmanPosition = obs.getPacmanPosition()
        if pacmanPosition.y == vector.y:
            if pacmanPosition.x < vector.x:
                return RIGHT
            else:
                return LEFT
        else:
            if pacmanPosition.y < vector.y:
                return DOWN
            else:
                return UP

    def __isOnNode__(self, obs: Observation) -> bool:
        pacmanPosition = obs.getPacmanPosition()
        mapPos = obs.map.createMapPosition(pacmanPosition)
        return not mapPos.isBetweenMapNodes

    def __isInDanger__(self, obs: Observation) -> bool:
        pacmanPosition = obs.getPacmanPosition()

        mapPos = obs.map.createMapPosition(pacmanPosition)
        dangerLevel = obs.calculateDangerLevel(mapPos.mapNode1.position, self.weightContainer)
        if mapPos.isBetweenMapNodes:
            dangerLevel = max(dangerLevel, obs.calculateDangerLevel(mapPos.mapNode2.position, self.weightContainer))

        # pacmanDangerLevel = obs.calculateDangerLevel(pacmanPosition, self.weightContainer)
        return dangerLevel > self.weightContainer.getWeight('fleeThreshold')

    def __collect_(self, obs: Observation) -> int:
        startMapNode, startIsCustom = obs.map.getOrCreateCustomMapNodeOnVector(obs.getPacmanPosition())

        maxPelletLevel = 0
        maxPelletDirection = STOP
        for neighborContainer in startMapNode.neighborContainers:
            endMapNode, path, distance = obs.map.getPathToEndOfDangerZoneInDirection(startMapNode,
                                                                                     neighborContainer.direction)

            if obs.isGhostInPath(path):
                continue

            pelletsInPath = obs.getPelletCountInPath(path)

            pathPelletLevel = obs.calculatePelletLevel(endMapNode.position, self.weightContainer) * (pelletsInPath + 1)

            if pathPelletLevel > maxPelletLevel:
                maxPelletLevel = pathPelletLevel
                maxPelletDirection = neighborContainer.direction

        if maxPelletLevel <= 1:
            nearestPelletPosition = obs.getNearestPelletPosition()
            nearestPelletMapNode = obs.map.getNearestMapNode(nearestPelletPosition, snapToGrid=False)
            pelletPath, _ = obs.map.calculateShortestPath(startMapNode.position, nearestPelletMapNode.position)

            if len(pelletPath) >= 2:
                maxPelletDirection = self.__getDirection__(obs, pelletPath[1])

        return maxPelletDirection

    def __flee__(self, obs: Observation) -> int:
        startMapNode, startIsCustom = obs.map.getOrCreateCustomMapNodeOnVector(obs.getPacmanPosition())

        minDangerLevel = 99999
        minDangerDirection = STOP
        for neighborContainer in startMapNode.neighborContainers:
            endMapNode, path, distance = obs.map.getPathToEndOfDangerZoneInDirection(startMapNode,
                                                                                     neighborContainer.direction)

            if obs.isGhostInPath(path):
                DebugHelper.drawPath(path, DebugHelper.RED, 5)
                continue
            DebugHelper.drawPath(path, DebugHelper.GREEN, 5)

            dangerLevel = obs.calculateDangerLevel(endMapNode.position, self.weightContainer)
            DebugHelper.drawDangerLevel(obs, endMapNode.position, self.weightContainer)

            if dangerLevel < minDangerLevel:
                minDangerLevel = dangerLevel
                minDangerDirection = neighborContainer.direction

        return minDangerDirection
