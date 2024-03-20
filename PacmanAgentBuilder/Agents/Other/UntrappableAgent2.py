import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Utils.Map import MapPosition
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class UntrappableAgent2(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

    def calculateNextMove(self, obs: Observation):

        # DebugHelper.drawMap(obs)
        # DebugHelper.drawDangerLevels(obs)
        # DebugHelper.drawGhostPaths(obs)

        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT

        return self.flee(obs, obs.map.createMapPosition(obs.getPacmanPosition()))

    def flee(self, obs: Observation, mapPos: MapPosition) -> int:
        startMapNode, startIsCustom = obs.map.getOrCreateCustomMapNodeOnVector(obs.getPacmanPosition())

        minDangerLevel = 99999
        minDangerDirection = STOP
        for neighborContainer in startMapNode.neighborContainers:
            endMapNode, path, distance = obs.map.getPathToEndOfDangerZoneInDirection(startMapNode,
                                                                                     neighborContainer.direction)

            if obs.isGhostInPath(path):
                # DebugHelper.drawPath(path, DebugHelper.RED, 5)
                continue
            # DebugHelper.drawPath(path, DebugHelper.GREEN, 5)

            dangerLevel = self.calculateDangerLevel(obs, mapPos, endMapNode.position, self.weightContainer)
            # DebugHelper.drawDangerLevel(dangerLevel, endMapNode.position)

            if dangerLevel < minDangerLevel:
                minDangerLevel = dangerLevel
                minDangerDirection = neighborContainer.direction

        return minDangerDirection

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
            if dist > weights.get('tooFarAwayThreshold'):
                continue

            totalDistance += dist

            # Threshold distance for a ghost to be considered 'close'
            if dist < weights.get('wayTooCloseThreshold'):
                numberOfReallyCloseGhosts += 1
            # Threshold distance for a ghost to be considered 'close'
            elif dist < weights.get('tooCloseThreshold'):
                numberOfCloseGhosts += 1

        # Adjust danger level based on the closest ghost
        closestGhostValue = (1 / (minDistance + 1)) * 1000 * (1 + weights.get('closestGhostMultiplier'))
        # Further adjust based on the number of close ghosts
        closeGhostValue = numberOfCloseGhosts * weights.get('tooCloseValue')
        closeGhostValue += numberOfReallyCloseGhosts * weights.get('wayTooCloseValue')
        # Calculate danger level
        dangerLevel = closestGhostValue + closeGhostValue

        # Danger zone multipliers
        if mapPos.isInDangerZone:
            dangerLevel *= 1 + weights.get('dangerZoneMultiplier')

            if mapPos.dangerZone.vectorIsMidMapNode(vector):
                dangerLevel *= 1 + weights.get('dangerZoneMiddleMapNodeMultiplier')

            if mapPos.dangerZone.ghostInDangerZone:
                dangerLevel *= 1 + weights.get('ghostInDangerZoneMultiplier')

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

    def getDirection(self, obs: Observation, target: Vector2) -> int:
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

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        return WeightContainer({
            'fleeThreshold': 0.01119,
            'pelletLevelDistance': 2.83253,
            'wayTooCloseThreshold': 32.68235,
            'tooCloseThreshold': 8e-05,
            'tooFarAwayThreshold': 1219.81699,
            'wayTooCloseValue': 352.64291,
            'tooCloseValue': 87.99661,
            'dangerZoneMultiplier': 8.68754,
            'dangerZoneMiddleMapNodeMultiplier': 0.00206,
            'ghostInDangerZoneMultiplier': 0.0,
            'closestGhostMultiplier': 0.0,
            'ghostIsCloserMultiplier': 3.11343,
            'edgeMultiplier': 1.75577
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
