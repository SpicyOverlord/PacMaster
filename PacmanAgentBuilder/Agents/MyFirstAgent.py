import random

import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacmanAgentBuilder.Genetics.WeightModifier import WeightModifier
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Iagent import IAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.Map import MapNode, MapPosition
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class MyFirstAgent(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

    def calculateNextMove(self, obs: Observation):
        mapPos = obs.map.createMapPosition(obs.getPacmanPosition())

        if self.__isInDanger__(obs, mapPos):
            return self.__flee__(obs, mapPos)

        elif self.isOnNode(mapPos):
            return self.__collect_(obs)

        # don't change direction
        return STOP

    def isOnNode(self, mapPos: MapPosition) -> bool:
        return not mapPos.isBetweenMapNodes

    def __isInDanger__(self, obs: Observation, mapPos: MapPosition) -> bool:
        dangerLevel = self.calculateDangerLevel(obs, mapPos, mapPos.mapNode1.position, self.weightContainer)
        if mapPos.isBetweenMapNodes:
            dangerLevel = max(dangerLevel,
                              self.calculateDangerLevel(obs, mapPos, mapPos.mapNode2.position, self.weightContainer))

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

            pathPelletLevel = self.calculatePelletLevel(obs, endMapNode.position, self.weightContainer) * (
                    pelletsInPath + 1)

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

    def __flee__(self, obs: Observation, mapPos: MapPosition) -> int:
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

            dangerLevel = self.calculateDangerLevel(obs, mapPos, endMapNode.position, self.weightContainer)
            DebugHelper.drawDangerLevel(dangerLevel, endMapNode.position)

            if dangerLevel < minDangerLevel:
                minDangerLevel = dangerLevel
                minDangerDirection = neighborContainer.direction

        return minDangerDirection

    def calculatePelletLevel(self, obs: Observation, vector: Vector2, weights: WeightContainer) -> float:
        minDistance = 99999
        totalDistance = 1.0

        for pellet in obs.pelletGroup.pelletList:
            dist = manhattanDistance(pellet.position, vector)
            if dist < weights.getWeight('pelletLevelDistance'):
                totalDistance += dist
                if dist < minDistance:
                    minDistance = dist
        for powerPellet in obs.pelletGroup.powerpellets:
            dist = manhattanDistance(powerPellet.position, vector)
            if dist < weights.getWeight('pelletLevelDistance'):
                totalDistance += dist
                if dist < minDistance:
                    minDistance = dist

        # if totalDistance == 0:
        #     return minDistance * 0.1
        return totalDistance / (minDistance + 1)

    def calculateDangerLevel(self, obs: Observation, mapPos: MapPosition,
                             vector: Vector2, weights: WeightContainer) -> float:

        minDistance = 9999999
        totalDistance = 0.0
        numberOfCloseGhosts = 0
        numberOfReallyCloseGhosts = 0

        for ghost in obs.getGhosts():
            # ignore ghost if it is not dangerous
            if ghost.mode.current in (FREIGHT, SPAWN) or isInCenterArea(ghost.position):
                continue

            path, dist = obs.map.calculateGhostPath(ghost=ghost, endVector=vector)

            # ignore ghost if it can't reach position (this normally only happens if the ghost is in the start area)
            if len(path) == 0:
                continue

            minDistance = min(minDistance, dist)

            # Threshold distance for a ghost to be considered 'too far away'
            # it will be ignored
            if dist > weights.getWeight('tooFarAwayThreshold'):
                continue

            totalDistance += dist

            # Threshold distance for a ghost to be considered 'close'
            if dist < weights.getWeight('wayTooCloseThreshold'):
                numberOfReallyCloseGhosts += 1
            # Threshold distance for a ghost to be considered 'close'
            elif dist < weights.getWeight('tooCloseThreshold'):
                numberOfCloseGhosts += 1

        # Adjust danger level based on the closest ghost
        closestGhostValue = (1 / (minDistance + 1)) * 1000 * (1 + weights.getWeight('closestGhostMultiplier'))
        # Further adjust based on the number of close ghosts
        closeGhostValue = numberOfCloseGhosts * weights.getWeight('tooCloseValue')
        closeGhostValue += numberOfReallyCloseGhosts * weights.getWeight('wayTooCloseValue')
        # Calculate danger level
        dangerLevel = closestGhostValue + closeGhostValue

        # Danger zone multipliers
        if mapPos.isInDangerZone:
            dangerLevel *= 1 + weights.getWeight('dangerZoneMultiplier')

            if mapPos.dangerZone.vectorIsMidMapNode(vector):
                dangerLevel *= 1 + weights.getWeight('dangerZoneMiddleMapNodeMultiplier')

            if mapPos.dangerZone.ghostInDangerZone:
                dangerLevel *= 1 + weights.getWeight('ghostInDangerZoneMultiplier')

        # a ghost is closer than pacman multiplier
        if obs.map.calculateDistance(obs.getPacmanPosition(), vector) > minDistance:
            dangerLevel *= 1 + weights.getWeight('ghostIsCloserMultiplier')

        # close to edge multiplier
        if distanceToNearestEdge(vector) < 40:
            dangerLevel *= 1 + weights.getWeight('edgeMultiplier')

        # Normalize based on total distance to avoid high values in less dangerous situations
        normalizedDanger = dangerLevel / (totalDistance + 1)

        # if normalizedDanger < 2:
        #     print("YES")
        return round(normalizedDanger, 5)

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

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        return WeightContainer({
            'fleeThreshold': 0.035,
            'pelletLevelDistance': 15.939,
            'wayTooCloseThreshold': 20.949,
            'tooCloseThreshold': 71.731,
            'tooFarAwayThreshold': 1979.009,
            'wayTooCloseValue': 4372.183,
            'tooCloseValue': 1363.13,
            'dangerZoneMultiplier': 0.005,
            'dangerZoneMiddleMapNodeMultiplier': 0.001,
            'ghostInDangerZoneMultiplier': 5.431,
            'closestGhostMultiplier': 0.144,
            'ghostIsCloserMultiplier': 2.612,
            'edgeMultiplier': 1.237
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
