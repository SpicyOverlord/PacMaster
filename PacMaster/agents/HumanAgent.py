import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.observation import Observation
from PacMaster.utils.utils import distanceToNearestEdge
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class HumanAgent(IAgent):
    def __init__(self, gameController):
        super().__init__(gameController)

    def calculateNextMove(self):
        obs = Observation(self.gameController)
        self.takeStats(obs)

        # pacmanPosition = obs.getPacmanPosition()

        # TEST
        DebugHelper.drawMap(obs)
        # DebugHelper.drawDangerLevels(obs)

        # DebugHelper.drawDangerLevel(obs, Vector2(180, 340))
        # dangerLevel = obs.calculateDangerLevel(Vector2(180, 340))
        # print(dangerLevel)

        # if mapPos.isInDangerZone:
        #     DebugHelper.drawDangerZone(mapPos.dangerZone)
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
