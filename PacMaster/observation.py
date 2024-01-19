import math
from Pacman_Complete.ghosts import *
from Pacman_Complete.nodes import Node


class Observation(object):
    def __init__(self, game):
        self.ghostGroup = game.ghosts
        self.pelletGroup = game.pellets
        self.nodes = game.nodes
        self.pacman = game.pacman

      # ------------------ Pacman Functions ------------------
    def getPacmanPosition(self):
        return self.pacman.position

    # ------------------ Node Functions ------------------
    def getNodes(self):
        return self.nodes

    def getNoteFromTiles(self, x, y) -> Node:
        return self.nodes.getNoteFromTiles((x, y))

    # ------------------ Pellet Functions ------------------
    def getPelletPositions(self):
        return [pellet.position for pellet in self.pelletGroup.pelletList]

    def getPowerPelletPositions(self):
        return [powerPellet.position for powerPellet in self.pelletGroup.powerpellets]

    def getClosestPelletPosition(self):
        return min(self.getPelletPositions(), key=lambda p: self.squaredDistance(p, self.pacman.position), default=None)

    def getClosestPowerPelletPosition(self):
        return min(self.getPowerPelletPositions(), key=lambda p: self.squaredDistance(p, self.pacman.position), default=None)

    # ------------------ Ghost Functions ------------------
    def getGhostMode(self):
        return self.ghostGroup.blinky.mode.current

    def getGhostPositions(self):
        return [self.ghostGroup.blinky.position, self.ghostGroup.pinky.position, self.ghostGroup.inky.position,
                self.ghostGroup.clyde.position]

    def getClosestGhostPosition(self):
        return min(self.getGhostPositions(), key=lambda g: self.squaredDistance(g, self.pacman.position), default=None)

    def getBlinky(self) -> Blinky:
        return self.ghostGroup.blinky

    def getPinky(self) -> Pinky:
        return self.ghostGroup.pinky

    def getInky(self) -> Inky:
        return self.ghostGroup.inky.position

    def getClyde(self) -> Inky:
        return self.ghostGroup.clyde.position

    # ------------------ Helper Functions ------------------
    def roundPosition(self, vector2: Vector2):
        return Vector2(round(vector2.x), round(vector2.y))

    def squaredDistance(self, a, b):
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

    def distance(self, a, b):
        return math.sqrt(self.squaredDistance(a, b))
