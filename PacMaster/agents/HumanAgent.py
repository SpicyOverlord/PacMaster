import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.observation import Observation
from Pacman_Complete.constants import *


class HumanAgent(IAgent):
    def __init__(self, gameController):
        super().__init__(gameController)

    def calculateNextMove(self):
        obs = Observation(self.gameController)
        self.takeStats(obs)

        # TEST
        # if self.actionsTaken % 10 == 0:
        #     print(obs.getPacmanPosition())

        # DebugHelper.drawMap(obs.map)
        mapPos = obs.map.createMapPosition(obs.getPacmanPosition())
        if mapPos.isInDangerZone:
            DebugHelper.drawDangerZone(mapPos.dangerZone)
        # DebugHelper.drawDot(mapPos.mapNode1.position, DebugHelper.YELLOW, 5)
        # if mapPos.isBetweenMapNodes:
        #     DebugHelper.drawDot(mapPos.mapNode2.position, DebugHelper.YELLOW, 5)

            # DebugHelper.pauseGame()

        # TEST

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
