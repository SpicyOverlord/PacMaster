from __future__ import annotations

from collections import Counter
from typing import Optional

from PacMaster.utils.map import Map, MapNode
from Pacman_Complete.constants import *
from Pacman_Complete.ghosts import Blinky, Ghost, Pinky, Inky, Clyde
from Pacman_Complete.vector import Vector2
from PacMaster.utils.utils import manhattenDistance, roundVector


class Observation(object):
    def __init__(self, game):
        self.ghostGroup = game.ghosts
        self.pelletGroup = game.pellets
        self.pacman = game.pacman
        self.map = Map(game.nodes)

    # ------------------ Pacman Functions ------------------
    def getPacmanPosition(self) -> Vector2:
        return roundVector(self.pacman.position)

    def getPacmanGoal(self) -> Vector2:
        return self.pacman.goal

    # ------------------ Map Functions ------------------

    def getMapNode(self, vector: Vector2 = None) -> MapNode:
        return self.map.getClosestMapNode(vector)

    def getMapNodes(self):
        return self.map.mapNodes

    def getClosestMapNode(self, vector: Vector2 = None) -> MapNode:
        if vector is None:
            vector = self.getPacmanPosition()

        return self.map.getClosestMapNode(vector)

    def getOnNode(self) -> MapNode | None:
        closestMapNode = self.getClosestMapNode()
        closestMapNodeDistance = manhattenDistance(self.getPacmanPosition(), closestMapNode.position)

        if closestMapNodeDistance < 10:
            return closestMapNode

        return None

    def getBetweenMapNodes(self) -> tuple[MapNode, MapNode, bool] | tuple[None, None, bool]:
        pacmanPosition = self.getPacmanPosition()
        for mapNode in self.map.mapNodes:
            if mapNode.position.x == pacmanPosition.x or mapNode.position.y == pacmanPosition.y:
                for neighbor in mapNode.neighbors:
                    if self.isBetweenMapNodes(mapNode.position, pacmanPosition, neighbor.mapNode.position):
                        return mapNode, neighbor.mapNode, mapNode.position.x == pacmanPosition.x

        return None, None, False

    def isBetweenMapNodes(self, mapNode1: MapNode, betweenVector: Vector2, mapNode2: MapNode) -> bool:
        if betweenVector.x == mapNode1.x and betweenVector.x == mapNode2.x and \
                min(mapNode1.y, mapNode2.y) <= betweenVector.y <= max(mapNode1.y, mapNode2.y):
            return True
        if betweenVector.y == mapNode1.y and betweenVector.y == mapNode2.y and \
                min(mapNode1.x, mapNode2.x) <= betweenVector.x <= max(mapNode1.x, mapNode2.x):
            return True

        return False

    # ------------------ Pellet Functions ------------------
    def getPelletsEaten(self) -> int:
        return self.pelletGroup.numEaten

    def getPelletPositions(self) -> list[Vector2]:
        return [pellet.position for pellet in self.pelletGroup.pelletList]

    def getPowerPelletPositions(self) -> list[Vector2]:
        return [powerPellet.position for powerPellet in self.pelletGroup.powerpellets]

    def getClosestPelletPosition(self) -> Vector2:
        return min(self.getPelletPositions(), key=lambda pellet: manhattenDistance(pellet, self.getPacmanPosition()),
                   default=None)

    def getClosestPowerPelletPosition(self) -> Vector2:
        return min(self.getPowerPelletPositions(),
                   key=lambda pellet: manhattenDistance(pellet, self.getPacmanPosition()),
                   default=None)

    # ------------------ Ghost Functions ------------------

    def getGhostBetweenMapNodes(self, mapNode1: MapNode, mapNode2: MapNode) -> Ghost:
        for ghost in self.getGhosts():
            if ghost.mode.current == FREIGHT:
                continue

            if ghost.position.x == mapNode1.x and ghost.position.x == mapNode2.x and \
                    min(mapNode1.y, mapNode2.y) <= ghost.position.y <= max(mapNode1.y, mapNode2.y):
                return ghost
            if ghost.position.y == mapNode1.y and ghost.position.y == mapNode2.y and \
                    min(mapNode1.x, mapNode2.x) <= ghost.position.x <= max(mapNode1.x, mapNode2.x):
                return ghost

        return None

    def getGhostModes(self) -> list[int]:
        return [ghost.mode.current for ghost in self.getGhosts()]

    def getGhostCommonMode(self) -> int:
        return Counter(self.getGhostModes()).most_common(1)[0][0]

    def getGhostCommonModeAsStr(self) -> str:
        modesMap = {SCATTER: "scatter", CHASE: "chase", FREIGHT: "freight", SPAWN: "spawn"}
        return modesMap[self.getGhostCommonMode()]

    def getGhostModesAsStr(self) -> list[str]:
        modesMap = {SCATTER: "scatter", CHASE: "chase", FREIGHT: "freight", SPAWN: "spawn"}
        return [modesMap.get(mode, f"unknown mode-int: '{mode}'") for mode in self.getGhostModes()]

    def getGhostPositions(self) -> list[Vector2]:
        return [roundVector(ghost.position) for ghost in self.getGhosts()]

    def getClosestGhostPosition(self, vector: Vector2 = None) -> Vector2:
        if vector is None:
            vector = self.getPacmanPosition()

        return min(self.getGhostPositions(), key=lambda ghost: manhattenDistance(ghost, vector),
                   default=None)

    def getGhosts(self) -> list[Ghost]:
        return [self.ghostGroup.blinky, self.ghostGroup.pinky, self.ghostGroup.inky, self.ghostGroup.clyde]

    def getBlinky(self) -> Blinky:
        return self.ghostGroup.blinky

    def getPinky(self) -> Pinky:
        return self.ghostGroup.pinky

    def getInky(self) -> Inky:
        return self.ghostGroup.inky

    def getClyde(self) -> Clyde:
        return self.ghostGroup.clyde

    # ------------------ Custom Functions ------------------
    def calculateDangerLevel(self, vector: Vector2 = None):
        if vector is None:
            vector = self.getPacmanPosition()

        dangerLevel = 0.0
        minDistance = 9999999
        totalDistance = 0.0
        numberOfCloseGhosts = 0
        dangerThreshold = 5  # Threshold distance for a ghost to be considered 'close'

        for ghost in self.getGhosts():
            # ignore ghost if it is in freight mode
            if ghost.mode.current == FREIGHT:
                continue

            distance = manhattenDistance(vector, roundVector(ghost.position))
            totalDistance += distance
            minDistance = min(minDistance, distance)

            if distance < dangerThreshold:
                numberOfCloseGhosts += 1

        # Adjust danger level based on the closest ghost
        dangerLevel += (1 / (minDistance + 1)) * 10000  # Adding 1 to avoid division by zero

        # Further adjust based on the number of close ghosts
        dangerLevel += numberOfCloseGhosts * 5000  # Weight for each close ghost

        # Normalize based on total distance to avoid high values in less dangerous situations
        normalizedDanger = dangerLevel / (totalDistance + 1)

        return normalizedDanger
