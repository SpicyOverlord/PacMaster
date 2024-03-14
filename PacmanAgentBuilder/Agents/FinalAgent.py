import random
from time import sleep

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


class FinalAgent(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

    def calculateNextMove(self, obs: Observation):
        mapPos = obs.map.createMapPosition(obs.getPacmanPosition())
        # sleep(0.03)
        # DebugHelper.drawMap(obs)
        # DebugHelper.drawDangerZone(mapPos.dangerZone)

        if self.isInDanger(obs, mapPos):
            return self.flee(obs, mapPos)

        elif self.isOnNode(mapPos):
            return self.collect(obs)

        # don't change direction
        return STOP

    def isOnNode(self, mapPos: MapPosition) -> bool:
        return not mapPos.isBetweenMapNodes

    def isInDanger(self, obs: Observation, mapPos: MapPosition) -> bool:
        dangerLevel = self.calculateDangerLevel(obs, mapPos, mapPos.mapNode1.position, self.weightContainer)
        if mapPos.isBetweenMapNodes:
            dangerLevel = max(dangerLevel,
                              self.calculateDangerLevel(obs, mapPos, mapPos.mapNode2.position, self.weightContainer))

        return dangerLevel > self.weightContainer.get('fleeThreshold')

    def collect(self, obs: Observation) -> int:
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

    def flee(self, obs: Observation, mapPos: MapPosition) -> int:
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
        for pellet in obs.pelletGroup.pelletList:
            dist = manhattanDistance(pellet.position, vector)
            if dist < weights.get('pelletLevelDistance'):
                return 1.0
        for powerPellet in obs.pelletGroup.powerpellets:
            dist = manhattanDistance(powerPellet.position, vector)
            if dist < weights.get('pelletLevelDistance'):
                return 1.0

        return 1.0 / 100000.0

    def calculateDangerLevel(self, obs: Observation, mapPos: MapPosition,
                             vector: Vector2, weights: WeightContainer) -> float:

        minDistance = 9999999
        totalDistance = 0.0
        ghostsDangerValue = 0.0
        numberOfCloseGhosts = 0

        for ghost in obs.getGhosts():
            # ignore ghost if it is not dangerous
            if ghost.mode.current in (FREIGHT, SPAWN) or isInCenterArea(ghost.position):
                continue

            path, dist = obs.map.calculateGhostPath(ghost=ghost, endVector=vector)

            # ignore ghost if it can't reach position (this normally only happens if the ghost is in the start area)
            if len(path) == 0:
                continue

            minDistance = min(minDistance, dist)

            # Threshold distance for a ghost to be considered 'too far away'. it will be ignored
            if dist > weights.get('tooFarAwayThreshold'):
                continue

            totalDistance += dist

            # Threshold distance for a ghost to be considered 'close'
            if dist < weights.get('tooCloseThreshold'):
                numberOfCloseGhosts += 1

            ghostWeight = 0
            if ghost.name == BLINKY:
                ghostWeight = weights.get('blinky')
            elif ghost.name == PINKY:
                ghostWeight = weights.get('pinky')
            elif ghost.name == INKY:
                ghostWeight = weights.get('inky')
            elif ghost.name == CLYDE:
                ghostWeight = weights.get('clyde')
            ghostsDangerValue += (1 + ghostWeight * weights.get('ghostMultiplier')) / (1 + dist)

        # Adjust danger level based on the closest ghost
        closestGhostValue = (1 / (minDistance + 1)) * 1000
        # Further adjust based on the number of close ghosts
        closeGhostValue = numberOfCloseGhosts * weights.get('tooCloseValue')

        # Calculate pellet level
        minDistance = 99999
        totalDistance = 1.0
        for pelletPosition in obs.getPelletPositions():
            dist = manhattanDistance(pelletPosition, vector)
            if dist < weights.get('pelletLevelDistanceInDangerLevel'):
                totalDistance += dist
                if dist < minDistance:
                    minDistance = dist
        for powerPelletPosition in obs.getPowerPelletPositions():
            dist = manhattanDistance(powerPelletPosition, vector)
            if dist < weights.get('pelletLevelDistanceInDangerLevel'):
                totalDistance += dist
                if dist < minDistance:
                    minDistance = dist
        pelletLevel = totalDistance / (minDistance + 1) * 0.001 * weights.get('pelletsInDangerLevelMultiplier')

        # distance to pacman
        distanceToPacman = manhattanDistance(vector, obs.getPacmanPosition()) * 0.001 * weights.get('distanceToPacManMultiplier')

        # Calculate danger level
        dangerLevel = closestGhostValue + closeGhostValue + ghostsDangerValue + distanceToPacman - pelletLevel
        print(
            f"danger: {dangerLevel}, "
            f"Closest ghost value: {closestGhostValue}, "
            f"close ghost value: {closeGhostValue}, "
            f"ghost danger value: {ghostsDangerValue}, "
            f"distance to pacman: {distanceToPacman}, "
            f"pellet level: {pelletLevel}"
        )

        # Danger zone multipliers
        if mapPos.isInDangerZone:
            dangerLevel *= 1 + weights.get('dangerZoneMultiplier')

            if mapPos.dangerZone.vectorIsMidMapNode(vector):
                dangerLevel *= 1 + weights.get('dangerZoneMiddleMapNodeMultiplier')

        # a ghost is closer than pacman multiplier
        if obs.map.calculateDistance(obs.getPacmanPosition(), vector) > minDistance:
            dangerLevel *= 1 + weights.get('ghostIsCloserMultiplier')

        # close to edge multiplier
        if distanceToNearestEdge(vector) < 40:
            dangerLevel *= 1 + weights.get('edgeMultiplier')
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
            # 'fleeThreshold': 0.018,
            'fleeThreshold': 5,
            'pelletLevelDistance': 0.702,
            'tooCloseThreshold': 25.613,
            'tooCloseValue': 412.091,
            'tooFarAwayThreshold': 4857.633,
            'dangerZoneMultiplier': 1.431,
            'dangerZoneMiddleMapNodeMultiplier': 0.458,
            'ghostIsCloserMultiplier': 10.304,
            'edgeMultiplier': 2.237,

            'pelletLevelDistanceInDangerLevel': 60,
            'pelletsInDangerLevelMultiplier': 1,
            'distanceToPacManMultiplier': 1,

            'ghostMultiplier': 10,
            'blinky': 1,
            'pinky': 1,
            'inky': 1,
            'clyde': 1,
        })

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        return WeightContainer({
            'fleeThreshold': 0.5,
            'pelletLevelDistance': 60,
            'tooCloseThreshold': 300,
            'tooCloseValue': 100,
            'tooFarAwayThreshold': 1000,
            'dangerZoneMultiplier': 1,
            'dangerZoneMiddleMapNodeMultiplier': 1,
            'ghostIsCloserMultiplier': 1,
            'edgeMultiplier': 1,

            'pelletLevelDistanceInDangerLevel': 60,
            'pelletsInDangerLevelMultiplier': 1,
            'distanceToPacManMultiplier': 1,

            'ghostMultiplier': 10,
            'blinky': 5,
            'pinky': 5,
            'inky': 5,
            'clyde': 5
        })
