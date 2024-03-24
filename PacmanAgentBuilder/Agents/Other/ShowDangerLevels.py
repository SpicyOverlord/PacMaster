import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Utils.Map import MapPosition
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class ShowDangerLevels(IAgent):
    """
    This is a simple agent that allows a human to play the game.
    """

    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

    def calculateNextMove(self, obs: Observation):

        DebugHelper.drawDot(obs.getPacmanPosition(), 5, DebugHelper.LIGHTBLUE)

        weights = ShowDangerLevels.getBestWeightContainer()
        for mapNode in obs.map.mapNodes:
            MapPos = obs.map.createMapPosition(mapNode.position)
            dangerLevel = self.calculateDangerLevel(obs, MapPos, MapPos.position, weights)
            DebugHelper.drawDangerLevel(dangerLevel, MapPos.position)

        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            return UP
        if key_pressed[K_DOWN]:
            return DOWN
        if key_pressed[K_LEFT]:
            return LEFT
        if key_pressed[K_RIGHT]:
            return RIGHT
        return STOP

    def calculateDangerLevel(self, obs: Observation, mapPos: MapPosition,
                             vector: Vector2, weights: WeightContainer) -> float:

        minGhostDistance = 9999999
        totalGhostDistance = 0.0
        ghostsDangerValue = 0.0
        numberOfCloseGhosts = 0

        for ghost in obs.getGhosts():
            # ignore ghost if it is not dangerous
            if ghost.mode.current in (FREIGHT, SPAWN) or isInCenterArea(ghost.position):
                continue

            ghostPath, ghostDistance = obs.map.calculateGhostPath(ghost=ghost, endVector=vector)

            # ignore ghost if it can't reach position (this normally only happens if the ghost is in the start area)
            if len(ghostPath) == 0:
                continue

            minGhostDistance = min(minGhostDistance, ghostDistance)

            # Threshold distance for a ghost to be considered 'too far away' to be considered
            if ghostDistance > weights.get('tooFarAwayThreshold'):
                continue

            totalGhostDistance += ghostDistance

            # Threshold distance for a ghost to be considered 'close'
            if ghostDistance < weights.get('tooCloseThreshold'):
                numberOfCloseGhosts += 1

            # for each ghost, calculate the 'ghost danger value' for that ghost based on its distance and weight
            ghostWeight = 0
            if ghost.name == BLINKY:
                ghostWeight = weights.get('blinky')
            elif ghost.name == PINKY:
                ghostWeight = weights.get('pinky')
            elif ghost.name == INKY:
                ghostWeight = weights.get('inky')
            elif ghost.name == CLYDE:
                ghostWeight = weights.get('clyde')
            ghostsDangerValue += ((1 + ghostWeight) * weights.get('ghostMultiplier')) / (1 + ghostDistance)

        # Calculate pellet level (basically how many pellets are around the position)
        minPelletDistance = 99999
        totalPelletDistance = 1.0
        for pelletPosition in obs.getPelletPositions():
            pelletDistance = manhattanDistance(pelletPosition, vector)
            if pelletDistance < weights.get('pelletLevelDistanceInDangerLevel'):
                totalPelletDistance += pelletDistance
                if pelletDistance < minPelletDistance:
                    minPelletDistance = pelletDistance
        for powerPelletPosition in obs.getPowerPelletPositions():
            pelletDistance = manhattanDistance(powerPelletPosition, vector)
            if pelletDistance < weights.get('pelletLevelDistanceInDangerLevel'):
                totalPelletDistance += pelletDistance
                if pelletDistance < minPelletDistance:
                    minPelletDistance = pelletDistance
        pelletLevel = totalPelletDistance / (minPelletDistance + 1) * 0.001 * weights.get(
            'pelletsInDangerLevelMultiplier')

        # distance to pacman
        distanceToPacman = manhattanDistance(vector, obs.getPacmanPosition()) * 0.001 * weights.get(
            'distanceToPacManMultiplier')
        # Adjust danger level based on the closest ghost
        closestGhostValue = (1 / (minGhostDistance + 1)) * 1000
        # Further adjust based on the number of close ghosts
        closeGhostValue = numberOfCloseGhosts * weights.get('tooCloseValue')

        # Calculate danger level (minus pellet level to make pacman flee towards pellets)
        dangerLevel = closestGhostValue + closeGhostValue + ghostsDangerValue + distanceToPacman - pelletLevel

        # Danger zone multipliers
        if mapPos.isInDangerZone:
            dangerLevel *= 1 + weights.get('dangerZoneMultiplier')
            if mapPos.dangerZone.vectorIsMidMapNode(vector):
                dangerLevel *= 1 + weights.get('dangerZoneMiddleMapNodeMultiplier')

        # a ghost is closer than pacman multiplier
        if obs.map.calculateDistance(obs.getPacmanPosition(), vector) > minGhostDistance:
            dangerLevel *= 1 + weights.get('ghostIsCloserMultiplier')

        # close to edge multiplier
        if distanceToNearestEdge(vector) < 40:
            dangerLevel *= 1 + weights.get('edgeMultiplier')

        # Normalize based on total distance to avoid high values in less dangerous situations
        normalizedDanger = dangerLevel / (totalGhostDistance + 1)

        return round(normalizedDanger, 5)

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        """
        :return: The best known weight container for this agent
        """
        return WeightContainer({
            'fleeThreshold': 10.3649,
            'pelletLevelDistance': 171.04447,
            'tooCloseThreshold': 0.55431,
            'tooCloseValue': 2.22647,
            'tooFarAwayThreshold': 0.00324,
            'dangerZoneMultiplier': 0.054,
            'dangerZoneMiddleMapNodeMultiplier': 0.00022,
            'ghostIsCloserMultiplier': 0.00322,
            'edgeMultiplier': 1.49241,
            'pelletLevelDistanceInDangerLevel': 619.93584,
            'pelletsInDangerLevelMultiplier': 0.18195,
            'distanceToPacManMultiplier': 0.0,
            'PelletIslandDistance': 0.0,
            'IslandSizeMultiplier': 9.89987,
            'IslandDistanceMultiplier': 1501.86886,
            'ghostMultiplier': 0.00022,
            'blinky': 0.00017,
            'pinky': 0.18026,
            'inky': 1e-05,
            'clyde': 0.0222
        })
