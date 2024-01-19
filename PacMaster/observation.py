import math
from Pacman_Complete.ghosts import *
from Pacman_Complete.nodes import Node, NodeGroup


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
    def getPelletPositions(self) -> list[Vector2]:
        return [pellet.position for pellet in self.pelletGroup.pelletList]

    def getPowerPelletPositions(self) -> list[Vector2]:
        return [powerPellet.position for powerPellet in self.pelletGroup.powerpellets]

    def getClosestPelletPosition(self) -> Vector2:
        return min(self.getPelletPositions(), key=lambda p: self.squaredDistance(p, self.pacman.position), default=None)

    def getClosestPowerPelletPosition(self) -> Vector2:
        return min(self.getPowerPelletPositions(), key=lambda p: self.squaredDistance(p, self.pacman.position),
                   default=None)

    # ------------------ Ghost Functions ------------------
    def getGhostModes(self) -> list[int]:
        return [ghost.mode.current for ghost in self.getGhosts()]

    def getGhostModesAsStr(self) -> list[str]:
        modesMap = {SCATTER: "scatter", CHASE: "chase", FREIGHT: "freight", SPAWN: "spawn"}
        return [modesMap.get(mode, f"unknown mode-int: '{mode}'") for mode in self.getGhostModes()]

    def getGhostPositions(self) -> list[Vector2]:
        return [ghost.position for ghost in self.getGhosts()]

    def getClosestGhostPosition(self) -> Vector2:
        return min(self.getGhostPositions(), key=lambda g: self.squaredDistance(g, self.pacman.position), default=None)

    def getGhosts(self) -> list[Ghost]:
        return [self.ghostGroup.blinky, self.ghostGroup.pinky, self.ghostGroup.inky,self.ghostGroup.clyde]

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

    def squaredDistance(self, a, b) -> int:
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

    def distance(self, a, b) -> float:
        return math.sqrt(self.squaredDistance(a, b))
