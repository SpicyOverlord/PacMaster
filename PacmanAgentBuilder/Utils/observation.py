from __future__ import annotations

from collections import Counter

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Utils.Map import Map, MapNode, MapPosition
from PacmanAgentBuilder.Utils.utils import manhattanDistance, isPortalPath, isInCenterArea, distanceToNearestEdge
from Pacman_Complete.constants import *
from Pacman_Complete.ghosts import Blinky, Ghost, Pinky, Inky, Clyde
from Pacman_Complete.nodes import Node
from Pacman_Complete.vector import Vector2


class Observation(object):
    """
    The Observation class contains all the necessary information that the agent will need to play the game:
    """

    def __init__(self, gameController, weightContainer: WeightContainer = None):
        self.ghostGroup = gameController.ghosts
        self.pelletGroup = gameController.pellets
        self.pacman = gameController.pacman
        self.nodeGroup = gameController.nodes

        self.map = Map(self, gameController.nodes, self.getGhosts())

    # ------------------ Pacman Functions ------------------

    # Returns Pac-Man's current position.
    def getPacmanPosition(self) -> Vector2:
        """
            :return: Pac-Man's current position.
        """
        if self.pacman.overshotTarget():
            return self.getPacmanTargetPosition()

        return Vector2(int(self.pacman.position.x), int(self.pacman.position.y))

    def getPacmanTargetPosition(self) -> Vector2:
        """
            :return: Returns the Node that Pac-Man is currently moving towards.
        """
        return self.pacman.target.position

    # ------------------ Node Functions ------------------
    def getNodeList(self) -> list[Node]:
        """
            :return: Returns a list of all nodes in the level.
        """
        return list(self.nodeGroup.nodesLUT.values())

    def getNodeFromVector(self, vector: Vector2) -> Node | None:
        """
            :param vector: The provided vector.
            :return: Returns the node at the provided vector. If no node is found, None is returned.
        """
        nodeKey = (int(vector.x), int(vector.y))
        if nodeKey in self.nodeGroup.nodesLUT.keys():
            return self.nodeGroup.nodesLUT[nodeKey]
        return None

    def getNodeNeighborList(self, node: Node) -> list[Node]:
        """
            :param node: The provided node.
            :return: Returns a list of the provided node's neighbors.
        """
        return [neighbor for neighbor in node.neighbors.values() if neighbor is not None]

    # ------------------ Pellet Functions ------------------
    def getPelletPositions(self) -> list[Vector2]:
        """
            :return: Returns a list of all non-eaten pellets' position.
        """
        return [pellet.position for pellet in self.pelletGroup.pelletList]

    def getPowerPelletPositions(self) -> list[Vector2]:
        """
            :return: Returns a list of all non-eaten power-pellets' position.
        """
        return [powerPellet.position for powerPellet in self.pelletGroup.powerpellets]

    def getNearestPelletPosition(self) -> Vector2:
        nearestPelletPosition = min(self.getPelletPositions(),
                                    key=lambda pellet: manhattanDistance(pellet, self.getPacmanPosition()),
                                    default=None)
        # in the rare case that the game hasn't registered that all pellets have been eaten.
        if nearestPelletPosition is None:
            return self.getPacmanPosition()
        return nearestPelletPosition

    def getNearestPowerPelletPosition(self) -> Vector2:
        return min(self.getPowerPelletPositions(),
                   key=lambda pellet: manhattanDistance(pellet, self.getPacmanPosition()),
                   default=None)

    def getPelletCountInPath(self, path: list[Vector2]) -> int:
        return sum(self.getPelletsBetweenVectors(path[i], path[i + 1]) for i in range(len(path) - 1))

    def getPelletsBetweenVectors(self, vector1: Vector2, vector2: Vector2) -> int:
        if isPortalPath(vector1, vector2):
            return 0

        pelletCount = 0
        for pelletPosition in self.getPelletPositions():
            if pelletPosition.x == vector1.x and pelletPosition.x == vector2.x and \
                    min(vector1.y, vector2.y) <= pelletPosition.y <= max(vector1.y, vector2.y):
                pelletCount += 1
            elif pelletPosition.y == vector1.y and pelletPosition.y == vector2.y and \
                    min(vector1.x, vector2.x) <= pelletPosition.x <= max(vector1.x, vector2.x):
                pelletCount += 1

        return pelletCount

    # ------------------ Ghost Functions ------------------
    def getGhostBetweenMapNodes(self, mapNode1: MapNode, mapNode2: MapNode) -> Ghost | None:
        return self.getGhostBetweenVectors(mapNode1.position, mapNode2.position)

    def getGhostBetweenVectors(self, vector1: Vector2, vector2: Vector2) -> Ghost | None:
        if isPortalPath(vector1, vector2):
            return None

        for ghost in self.getGhosts():
            if ghost.mode.current in (FREIGHT, SPAWN):
                continue

            if ghost.position.x == vector1.x and ghost.position.x == vector2.x and \
                    min(vector1.y, vector2.y) <= ghost.position.y <= max(vector1.y, vector2.y):
                return ghost
            if ghost.position.y == vector1.y and ghost.position.y == vector2.y and \
                    min(vector1.x, vector2.x) <= ghost.position.x <= max(vector1.x, vector2.x):
                return ghost

        return None

    def isGhostInPath(self, path: list[Vector2]) -> bool:
        for i in range(len(path) - 1):
            startVector = path[i]
            endVector = path[i + 1]

            if self.getGhostBetweenVectors(startVector, endVector) is not None:
                return True

        return False

    def getGhostModes(self) -> list[int]:
        """
            :return: Returns a list of all ghosts' modes.
        """
        return [ghost.mode.current for ghost in self.getGhosts()]

    def getGhostCommonMode(self) -> int:
        """
            :return: Returns the mode that most ghosts are in (CHASE, SCATTER, etc.).
        """
        return Counter(self.getGhostModes()).most_common(1)[0][0]

    def getGhosts(self) -> list[Ghost]:
        """
            :return: Returns a list of the ghost objects.
        """
        return [self.getBlinky(), self.getPinky(), self.getInky(), self.getClyde()]

    def getGhostPositions(self) -> list[Vector2]:
        """
            :return: Returns a list of the ghosts' positions.
        """
        return [Vector2(round(ghost.position.x), round(ghost.position.y)) for ghost in self.getGhosts()]

    def getClosestGhost(self, vector: Vector2 = None) -> Ghost:
        if vector is None:
            vector = self.getPacmanPosition()

        # return the closest ghost to the given vector
        closestGhost = None
        closestGhostDistance = 9999999
        for ghost in self.getGhosts():
            if isInCenterArea(ghost.position):
                continue

            ghostDistance = self.map.calculateGhostDistance(ghost, vector)
            if ghostDistance < closestGhostDistance:
                closestGhost = ghost
                closestGhostDistance = ghostDistance

        return closestGhost

    def getGhost(self, ghost: int) -> Ghost:
        """
            :param ghost: The provided ghost constant (BLINKY, PINKY, etc.)
            :return: Returns a ghost object from the provided ghost constant.
        """
        if ghost == BLINKY:
            return self.getBlinky()
        elif ghost == PINKY:
            return self.getPinky()
        elif ghost == INKY:
            return self.getInky()
        elif ghost == CLYDE:
            return self.getClyde()
        else:
            raise Exception(f"Unknown ghost: {ghost}")

    def getBlinky(self) -> Blinky:
        """
            :return: Returns the Blinky object.
        """
        return self.ghostGroup.blinky

    def getPinky(self) -> Pinky:
        """
            :return: Returns the Pinky object.
        """
        return self.ghostGroup.pinky

    def getInky(self) -> Inky:
        """
            :return: Returns the Inky object.
        """
        return self.ghostGroup.inky

    def getClyde(self) -> Clyde:
        """
            :return: Returns the Clyde object.
        """
        return self.ghostGroup.clyde

    # ------------------ Custom Functions ------------------
    def calculatePelletLevel(self, vector: Vector2, weights: WeightContainer) -> float:
        minDistance = 99999
        totalDistance = 1.0

        for pellet in self.pelletGroup.pelletList:
            dist = manhattanDistance(pellet.position, vector)
            if dist < weights.getWeight('pelletLevelDistance'):
                totalDistance += dist
                if dist < minDistance:
                    minDistance = dist
        for powerPellet in self.pelletGroup.powerpellets:
            dist = manhattanDistance(powerPellet.position, vector)
            if dist < weights.getWeight('pelletLevelDistance'):
                totalDistance += dist
                if dist < minDistance:
                    minDistance = dist

        # if totalDistance == 0:
        #     return minDistance * 0.1
        return totalDistance / (minDistance + 1)

    def calculateDangerLevel(self, vector: Vector2, weights: WeightContainer) -> float:
        minDistance = 9999999
        totalDistance = 0.0
        numberOfCloseGhosts = 0
        numberOfReallyCloseGhosts = 0

        for ghost in self.getGhosts():
            # ignore ghost if it is not dangerous
            if ghost.mode.current in (FREIGHT, SPAWN) or isInCenterArea(ghost.position):
                continue

            path, dist = self.map.calculateGhostPath(ghost=ghost, endVector=vector)

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
        # TODO: comment this and see if it actually makes the Agents better
        mapPos = MapPosition(self.map, vector)
        if mapPos.isInDangerZone:
            dangerLevel *= 1 + weights.getWeight('dangerZoneMultiplier')

            if mapPos.dangerZone.vectorIsMidMapNode(vector):
                dangerLevel *= 1 + weights.getWeight('dangerZoneMiddleMapNodeMultiplier')

            if mapPos.dangerZone.ghostInDangerZone:
                dangerLevel *= 1 + weights.getWeight('ghostInDangerZoneMultiplier')

        # a ghost is closer than pacman multiplier
        if self.map.calculateDistance(self.getPacmanPosition(), vector) > minDistance:
            dangerLevel *= 1 + weights.getWeight('ghostIsCloserMultiplier')

        # close to edge multiplier
        if distanceToNearestEdge(vector) < 40:
            dangerLevel *= 1 + weights.getWeight('edgeMultiplier')

        # Normalize based on total distance to avoid high values in less dangerous situations
        normalizedDanger = dangerLevel / (totalDistance + 1)

        # if normalizedDanger < 2:
        #     print("YES")
        return round(normalizedDanger, 5)
