from __future__ import annotations

from collections import Counter
from typing import Optional

from PacMaster.utils.map import Map, MapNode, MapPosition
from Pacman_Complete.constants import *
from Pacman_Complete.ghosts import Blinky, Ghost, Pinky, Inky, Clyde
from Pacman_Complete.vector import Vector2
from PacMaster.utils.utils import manhattanDistance, roundVector


class Observation(object):
    def __init__(self, gameController):
        self.ghostGroup = gameController.ghosts
        self.pelletGroup = gameController.pellets
        self.pacman = gameController.pacman
        self.map = Map(self, gameController.nodes, self.getGhosts())

    # ------------------ Pacman Functions ------------------
    def getPacmanPosition(self) -> Vector2:
        if self.pacman.overshotTarget():
            return self.getPacmanTarget()

        return roundVector(self.pacman.position)

    def getPacmanTarget(self) -> Vector2:
        return self.pacman.target.position

    # ------------------ Pellet Functions ------------------
    def getPelletsEaten(self) -> int:
        return self.pelletGroup.numEaten

    def getPelletPositions(self) -> list[Vector2]:
        return [pellet.position for pellet in self.pelletGroup.pelletList]

    def getPowerPelletPositions(self) -> list[Vector2]:
        return [powerPellet.position for powerPellet in self.pelletGroup.powerpellets]

    def getClosestPelletPosition(self) -> Vector2:
        return min(self.getPelletPositions(), key=lambda pellet: manhattanDistance(pellet, self.getPacmanPosition()),
                   default=None)

    def getClosestPowerPelletPosition(self) -> Vector2:
        return min(self.getPowerPelletPositions(),
                   key=lambda pellet: manhattanDistance(pellet, self.getPacmanPosition()),
                   default=None)

    # ------------------ Ghost Functions ------------------

    def getGhostBetweenMapNodes(self, mapNode1: MapNode, mapNode2: MapNode) -> Ghost | None:
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

    def getClosestGhost(self, vector: Vector2 = None) -> Ghost:
        if vector is None:
            vector = self.getPacmanPosition()

        # return the closest ghost to the given vector
        closestGhost = None
        closestGhostDistance = 9999999
        for ghost in self.getGhosts():
            distance = self.map.calculateDistance(ghost.position, vector, True, ghost.direction)
            if distance < closestGhostDistance:
                closestGhost = ghost
                closestGhostDistance = distance

        return closestGhost

    def getGhosts(self) -> list[Ghost]:
        return [self.getBlinky(), self.getPinky(), self.getInky(), self.getClyde()]

    def getGhost(self, ghost: int) -> Ghost:
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

        wayTooCloseThreshold = TILEWIDTH * 3  # Threshold distance for a ghost to be considered 'close'
        tooCloseThreshold = TILEWIDTH * 5  # Threshold distance for a ghost to be considered 'close'
        tooFarAwayThreshold = TILESIZE * 17  # Threshold distance for a ghost to be considered 'too far away'
        dangerZoneMultiplier = 3  # Multiplier for danger level if vector is in danger zone
        ghostInDangerZoneMultiplier = 10  # Multiplier for danger level if ghost is in danger zone

        minDistance = 9999999
        totalDistance = 0.0
        numberOfCloseGhosts = 0
        numberOfReallyCloseGhosts = 0

        for ghost in self.getGhosts():
            # ignore ghost if it is in freight mode
            if ghost.mode.current in (FREIGHT, SPAWN):
                continue

            distance = self.map.calculateDistance(vector, roundVector(ghost.position))

            # ignore ghost if it is too far away
            if distance > tooFarAwayThreshold:
                continue

            totalDistance += distance
            minDistance = min(minDistance, distance)

            if distance < wayTooCloseThreshold:
                numberOfReallyCloseGhosts += 1
            elif distance < tooCloseThreshold:
                numberOfCloseGhosts += 1

        # Adjust danger level based on the closest ghost
        closestGhostValue = (1 / (minDistance + 1)) * 50000  # Adding 1 to avoid division by zero
        # Further adjust based on the number of close ghosts
        closeGhostValue = numberOfCloseGhosts * 200  # Weight for each close ghost
        closeGhostValue += numberOfReallyCloseGhosts * 500
        # Calculate danger level
        dangerLevel = closestGhostValue + closeGhostValue

        mapPos = MapPosition(self.map, vector)
        if mapPos.isInDangerZone:
            dangerLevel *= dangerZoneMultiplier
            if mapPos.dangerZone.isGhostInDangerZone:
                dangerLevel *= ghostInDangerZoneMultiplier

        # Normalize based on total distance to avoid high values in less dangerous situations
        normalizedDanger = dangerLevel / (totalDistance + 1)

        return round(normalizedDanger, 5)
