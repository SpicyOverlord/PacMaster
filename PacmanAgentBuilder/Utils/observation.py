from __future__ import annotations

from collections import Counter
from typing import List

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

    def __init__(self, gameController):
        self.ghostGroup = gameController.ghosts
        self.pelletGroup = gameController.pellets
        self.pacman = gameController.pacman
        self.nodeGroup = gameController.nodes
        self.currentLevel = gameController.level
        self.gameController = gameController

        self.map = Map(self, gameController.nodes)

    def getLegalMoves(self) -> list[int]:
        """
            :return: Returns the legal moves from Pacman's current position
        """
        pacmanPosition = self.getPacmanPosition()
        pacmanTargetPosition = self.getPacmanTargetPosition()
        legalMoves = []
        # if pacman is on a node we get the neighbors
        if pacmanPosition.x == pacmanTargetPosition.x and pacmanPosition.y == pacmanTargetPosition.y:
            for i in self.getNodeFromVector(pacmanPosition).neighbors:
                if self.getNodeFromVector(pacmanPosition).neighbors[i] is not None:
                    legalMoves.append(i)
        # if pacman is left or right of node
        if pacmanPosition.x != pacmanTargetPosition.x:
            legalMoves.append(LEFT)
            legalMoves.append(RIGHT)
        # if pacman is above or below node
        elif pacmanPosition.y != pacmanTargetPosition.y:
            legalMoves.append(UP)
            legalMoves.append(DOWN)
        return legalMoves

    def getRemainingLives(self):
        """
            :return: Returns the remaining lives of Pacman
        """
        return self.gameController.lives


    @staticmethod
    def isVectorBetweenVectors(vector1: Vector2, vector2: Vector2, middleVector: Vector2) -> bool:
        """
        Checks if a vector is between two other vectors.
        :param vector1: The first vector.
        :param vector2: The second vector.
        :param middleVector: The middle vector.
        :return: True if the middle vector is between the two vectors, False otherwise.
        """
        if middleVector.x == vector1.x and middleVector.x == vector2.x and \
                min(vector1.y, vector2.y) <= middleVector.y <= max(vector1.y, vector2.y) or \
                middleVector.y == vector1.y and middleVector.y == vector2.y and \
                min(vector1.x, vector2.x) <= middleVector.x <= max(vector1.x, vector2.x):
            return True
        return False

    def isVectorInPath(self, path: list[Vector2], vector: Vector2) -> bool:
        """
        :param path: The path.
        :param vector: The vector.
        :return: True if the vector is in the path, False otherwise.
        """
        if len(path) < 2:
            return False

        for i in range(len(path) - 1):
            startVector = path[i]
            endVector = path[i + 1]

            if self.isVectorBetweenVectors(startVector, endVector, vector):
                return True

        return False

    # ------------------ Pacman Functions ------------------

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
        pacmanPosition = self.getPacmanPosition()
        nearestPelletPosition = min(self.getPelletPositions(),
                                    key=lambda pellet: manhattanDistance(pellet, pacmanPosition),
                                    default=None)
        # in the rare case that the game hasn't registered that all pellets have been eaten.
        if nearestPelletPosition is None:
            return pacmanPosition
        return nearestPelletPosition

    def getNearestXPelletPosition(self, x: int) -> List[Vector2]:
        pacmanPosition = self.getPacmanPosition()
        pelletPositions = self.getPelletPositions()
        pelletPositions.sort(key=lambda pellet: manhattanDistance(pellet, pacmanPosition))
        nearest_pellets = pelletPositions[:x]

        if len(nearest_pellets) < x:
            nearest_pellets += [Vector2(0, 0)] * (x - len(nearest_pellets))
        return nearest_pellets

    def getNearestPowerPelletPosition(self) -> Vector2:
        return min(self.getPowerPelletPositions(),
                   key=lambda pellet: manhattanDistance(pellet, self.getPacmanPosition()),
                   default=None)

    def getPelletCountInPath(self, path: list[Vector2]) -> int:
        return sum(self.getPelletsBetweenVectors(path[i], path[i + 1]) for i in range(len(path) - 1))

    def getPelletsBetweenVectors(self, vector1: Vector2, vector2: Vector2) -> int:
        """
        :param vector1: The first vector.
        :param vector2: The second vector.
        :return: The number of pellets between the two vectors.
        """
        # if the path is a portal path, return 0
        if isPortalPath(vector1, vector2):
            return 0

        pelletCount = 0
        for pelletPosition in self.getPelletPositions():
            if self.isVectorBetweenVectors(vector1, vector2, pelletPosition):
                pelletCount += 1

        return pelletCount

    # ------------------ Ghost Functions ------------------
    def getGhostBetweenMapNodes(self, mapNode1: MapNode, mapNode2: MapNode) -> Ghost | None:
        """
        :param mapNode1: The first map node.
        :param mapNode2: The second map node.
        :return: a ghost if the ghost is between the two MapNodes, else None
        """
        return self.getGhostBetweenVectors(mapNode1.position, mapNode2.position)

    def getGhostBetweenVectors(self, vector1: Vector2, vector2: Vector2) -> Ghost | None:
        """
        :param vector1: The first vector.
        :param vector2: The second vector.
        :return: a ghost if the ghost is between the two Vector2, else None
        """
        # skip if the path between the vectors is a portal path
        if isPortalPath(vector1, vector2):
            return None

        for ghost in self.getGhosts():
            # skip if the ghost is in freight or spawn mode
            if ghost.mode.current in (FREIGHT, SPAWN):
                continue

            if self.isVectorBetweenVectors(vector1, vector2, ghost.position):
                return ghost

        return None

    def isGhostInPath(self, path: list[Vector2]) -> bool:
        """
        :param path: The path.
        :return: True if a ghost is in the path, False otherwise.
        """
        for ghost in self.getGhosts():
            if ghost.mode.current in (FREIGHT, SPAWN) or isInCenterArea(ghost.position):
                continue
            if self.isVectorInPath(path, ghost.position):
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
        """
        :param vector: The vector.
        :return: Returns the closest ghost to the given vector.
        """
        if vector is None:
            vector = self.getPacmanPosition()

        closestGhost = None
        closestGhostDistance = 9999999
        for ghost in self.getGhosts():
            # ignore ghost if it is in the center area
            if isInCenterArea(ghost.position):
                continue

            _, ghostDistance = self.map.calculateGhostPath(ghost, vector)
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
