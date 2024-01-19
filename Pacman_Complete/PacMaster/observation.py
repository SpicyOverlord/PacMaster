import math

from ghosts import *


class Observation(object):
    def __init__(self, game):
        self.ghostGroup = game.ghosts
        self.pelletGroup = game.pellets
        self.pacman = game.pacman

    def getGhostMode(self):
        return self.ghostGroup.blinky.mode.current

    def getPelletPositions(self):
        return [pellet.position for pellet in self.pelletGroup.pelletList]

    def getPowerPelletPositions(self):
        return [powerPellet.position for powerPellet in self.pelletGroup.powerpellets]

    def getGhostPositions(self):
        return [self.ghostGroup.blinky.position, self.ghostGroup.pinky.position, self.ghostGroup.inky.position,
                self.ghostGroup.clyde.position]

    def getPacmanPosition(self):
        return self.pacman.position

    def getClosestGhostPosition(self):
        return min(self.getGhostPositions(), key=lambda g: self.squaredDistance(g, self.pacman.position), default=None)

    def getClosestPelletPosition(self):
        return min(self.getPelletPositions(), key=lambda p: self.squaredDistance(p, self.pacman.position), default=None)

    def getBlinky(self) -> Blinky:
        return self.ghostGroup.blinky

    def getPinky(self) -> Pinky:
        return self.ghostGroup.pinky

    def getInky(self) -> Inky:
        return self.ghostGroup.inky.position

    def getClyde(self) -> Inky:
        return self.ghostGroup.clyde.position

    def squaredDistance(self, a, b):
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

    def distance(self, a, b):
        return math.sqrt(self.squaredDistance(a, b))
