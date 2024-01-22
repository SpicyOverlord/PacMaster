from collections import Counter

from Pacman_Complete.constants import SCATTER, CHASE, FREIGHT, SPAWN
from Pacman_Complete.ghosts import Blinky, Ghost, Pinky, Inky, Clyde
from Pacman_Complete.nodes import Node, NodeGroup
from Pacman_Complete.vector import Vector2


class Observation(object):
    def __init__(self, game):
        self.ghostGroup = game.ghosts
        self.pelletGroup = game.pellets
        self.nodes = game.nodes
        self.pacman = game.pacman

    # ------------------ Pacman Functions ------------------
    def getPacmanPosition(self) -> Vector2:
        return self.pacman.position

    # ------------------ Node Functions ------------------
    def getNodeGroup(self) -> NodeGroup:
        return self.nodes

    def getNoteFromTiles(self, x, y) -> Node:
        return self.nodes.getNoteFromTiles((x, y))

    # ------------------ Pellet Functions ------------------
    def getPelletsEaten(self) -> int:
        return self.pelletGroup.numEaten
    def getPelletPositions(self) -> list[Vector2]:
        return [pellet.position for pellet in self.pelletGroup.pelletList]

    def getPowerPelletPositions(self) -> list[Vector2]:
        return [powerPellet.position for powerPellet in self.pelletGroup.powerpellets]

    def getClosestPelletPosition(self) -> Vector2:
        return min(self.getPelletPositions(), key=lambda p: self.manhattenDistance(p, self.pacman.position),
                   default=None)

    def getClosestPowerPelletPosition(self) -> Vector2:
        return min(self.getPowerPelletPositions(), key=lambda p: self.manhattenDistance(p, self.pacman.position),
                   default=None)

    # ------------------ Ghost Functions ------------------
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
        return [ghost.position for ghost in self.getGhosts()]

    def getClosestGhostPosition(self) -> Vector2:
        return min(self.getGhostPositions(), key=lambda g: self.manhattenDistance(g, self.pacman.position),
                   default=None)

    def getGhosts(self) -> list[Ghost]:
        return [self.ghostGroup.blinky, self.ghostGroup.pinky, self.ghostGroup.inky, self.ghostGroup.clyde]

    def getBlinky(self) -> Blinky:
        return self.ghostGroup.blinky

    def getPinky(self) -> Pinky:
        return self.ghostGroup.pinky

    def getInky(self) -> Inky:
        return self.ghostGroup.inky.position

    def getClyde(self) -> Clyde:
        return self.ghostGroup.clyde.position

    # ------------------ Helper Functions ------------------
    def roundPosition(self, vector2: Vector2) -> Vector2:
        return Vector2(round(vector2.x), round(vector2.y))

    def manhattenDistance(self, a: Vector2, b: Vector2) -> int:
        return abs(a.x - b.x) + abs(a.y - b.y)

    # ------------------ Custom Functions ------------------
    def CalculateDangerLevel(self):

        dangerLevel = 0.0
        minDistance = 9999999
        totalDistance = 0.0
        numberOfCloseGhosts = 0
        dangerThreshold = 5  # Threshold distance for a ghost to be considered 'close'

        for ghost in self.getGhosts():
            # ignore ghost if it is in freight mode
            if ghost.mode.current == FREIGHT:
                continue

            distance = self.manhattenDistance(self.pacman.position, ghost.position)
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
