import random

import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacMaster.Genetics.WeightModifier import WeightModifier
from PacMaster.Genetics.WeightContainer import WeightContainer
from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.map import MapNode
from PacMaster.utils.observation import Observation
from PacMaster.utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class FirstRealAgent(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController)

        if weightContainer is None:
            self.weightContainer = FirstRealAgent.getBestWeightContainer()
        else:
            self.weightContainer = weightContainer

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
        # return WeightContainer({
        #     'fleeThreshold': 0.192,
        #     'pelletLevelDistance': 1.126,
        #     'wayTooCloseThreshold': 77.053,
        #     'tooCloseThreshold': 207.475,
        #     'tooFarAwayThreshold': 1167.487,
        #     'wayTooCloseValue': 700.586,
        #     'tooCloseValue': 29.333,
        #     'dangerZoneMultiplier': 1.579,
        #     'dangerZoneMiddleMapNodeMultiplier': 0.279,
        #     'ghostInDangerZoneMultiplier': 2.024,
        #     'closestGhostMultiplier': 0.52,
        #     'ghostIsCloserMultiplier': 1.373,
        #     'edgeMultiplier': 2.123
        # })

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

    def calculateNextMove(self):
        obs = Observation(self.gameController, self.weightContainer)
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

        DebugHelper.drawMap(obs)
        DebugHelper.drawDangerLevels(obs)

        pacmanPosition = obs.getPacmanPosition()

        mapPos = obs.map.createMapPosition(pacmanPosition)
        dangerLevel = obs.calculateDangerLevel(mapPos.mapNode1.position)
        if mapPos.isBetweenMapNodes:
            dangerLevel = max(dangerLevel, obs.calculateDangerLevel(mapPos.mapNode2.position))

        # pacmanDangerLevel = obs.calculateDangerLevel(pacmanPosition)
        if dangerLevel > self.weightContainer.getWeight('fleeThreshold'):
            return self.__getLeastDangerousDirectionFromCustomNode__(obs)

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

            if len(pelletPath) >= 2:
                maxPelletDirection = self.__getDirection__(obs, pelletPath[1])

        return maxPelletDirection

    def __getLeastDangerousDirectionFromCustomNode__(self, obs: Observation) -> int:
        startMapNode, startIsCustom = obs.map.getOrCreateCustomMapNodeOnVector(obs.getPacmanPosition())

        minDangerLevel = 99999
        minDangerDirection = STOP
        for neighborContainer in startMapNode.neighborContainers:
            endMapNode, path, distance = obs.map.getPathToEndOfDangerZoneInDirection(startMapNode,
                                                                                     neighborContainer.direction)

            if obs.isGhostInPath(path):
                DebugHelper.drawPath(path, DebugHelper.RED, 5)
                # DebugHelper.pauseGame()
                continue

            DebugHelper.drawPath(path, DebugHelper.GREEN, 5)

            dangerLevel = obs.calculateDangerLevel(endMapNode.position)
            if dangerLevel < minDangerLevel:
                minDangerLevel = dangerLevel
                minDangerDirection = neighborContainer.direction

        return minDangerDirection
