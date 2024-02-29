import random

import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacMaster.Genetic.WeightModifier import WeightModifier
from PacMaster.Genetic.WeightContainer import WeightContainer
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
            self.weightContainer = FirstRealAgent.getDefaultWeightContainer()
        else:
            self.weightContainer = weightContainer

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        return WeightContainer({'fleeThreshold': 0.166, 'pelletLevelDistance': -0.91, 'wayTooCloseThreshold': 40.464,
                                'tooCloseThreshold': 206.539, 'tooFarAwayThreshold': 102.199,
                                'wayTooCloseValue': 329.268, 'tooCloseValue': 82.789, 'dangerZoneMultiplier': 1.606,
                                'dangerZoneMiddleMapNodeMultiplier': 1.826, 'ghostInDangerZoneMultiplier': 3.604,
                                'closestGhostMultiplier': 50.886, 'ghostIsCloserMultiplier': 2.889,
                                'edgeMultiplier': 0.641})

        # return WeightContainer({
        #     'fleeThreshold': 0.2,
        #     'pelletLevelDistance': -5,
        #     'wayTooCloseThreshold': 275,
        #     'tooCloseThreshold': 400,
        #     'tooFarAwayThreshold': 900,
        #     'wayTooCloseValue': 150,
        #     'tooCloseValue': 150,
        #     'dangerZoneMultiplier': 1.3,
        #     'dangerZoneMiddleMapNodeMultiplier': 2,
        #     'ghostInDangerZoneMultiplier': 2,
        #     'closestGhostMultiplier': 2,
        #     'ghostIsCloserMultiplier': 1.5,
        #     'edgeMultiplier': 1})

        # return WeightContainer({
        #     'fleeThreshold': 0.094,
        #     'pelletLevelDistance': 61.683,
        #     'wayTooCloseThreshold': 89.229,
        #     'tooCloseThreshold': 205.579,
        #     'tooFarAwayThreshold': 403.254,
        #     'wayTooCloseValue': 492.364,
        #     'tooCloseValue': 260.789,
        #     'dangerZoneMultiplier': 6.325,
        #     'dangerZoneMiddleMapNodeMultiplier': 0.983,
        #     'ghostInDangerZoneMultiplier': 12.141,
        #     'closestGhostMultiplier': 45.16,
        #     'ghostIsCloserMultiplier': 1.685,
        #     'edgeMultiplier': 1.987}
        # )

        # return WeightContainer({
        #     'fleeThreshold': 0.1,
        #
        #     'pelletLevelDistance': 3 * TILESIZE,
        #
        #     'wayTooCloseThreshold': TILEWIDTH * 6,
        #     'tooCloseThreshold': TILEWIDTH * 12,
        #     'tooFarAwayThreshold': TILESIZE * 18,
        #     'wayTooCloseValue': 400,
        #     'tooCloseValue': 200,
        #     'dangerZoneMultiplier': 5,
        #     'dangerZoneMiddleMapNodeMultiplier': 1.2,
        #     'ghostInDangerZoneMultiplier': 10,
        #     'closestGhostMultiplier': 50,
        #     'ghostIsCloserMultiplier': 1.5,
        #     'edgeMultiplier': 2
        # })

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
        # DebugHelper.drawDangerLevels(obs)

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
