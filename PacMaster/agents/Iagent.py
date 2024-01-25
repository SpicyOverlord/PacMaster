from abc import abstractmethod, ABC

from PacMaster.utils.debugDrawer import DebugDrawer
from PacMaster.utils.observation import Observation
from Pacman_Complete.constants import *


class IAgent(ABC):
    @abstractmethod
    def __init__(self, gameController):
        self.gameController = gameController
        self.actionsTaken = 0
        self.pelletsEatenThisLevel = 0

    @abstractmethod
    def calculateNextMove(self):
        raise Exception("NotImplementedException")

    def takeStats(self, obs: Observation):
        self.actionsTaken += 1
        self.pelletsEatenThisLevel = obs.getPelletsEaten()
        pass

    def drawGhostPaths(self, obs: Observation):
        for ghost in obs.getGhosts():
            self.drawGhostPath(obs, ghost.name)

    def drawGhostPath(self, obs: Observation, ghostName: int = BLINKY):
        ghost = obs.getGhost(ghostName)

        if ghost.mode.current == FREIGHT:
            return

        lineColor = (255, 255, 255)
        width = 5
        if ghostName == BLINKY:
            lineColor = RED
            width = 7
        elif ghostName == PINKY:
            lineColor = PINK
            width = 6
        elif ghostName == INKY:
            lineColor = TEAL
            width = 5
        elif ghostName == CLYDE:
            lineColor = ORANGE
            width = 4

        path, _ = obs.map.getShortestPath(ghost.position, ghost.goal)
        DebugDrawer.drawDashedPath(path, lineColor, width)
