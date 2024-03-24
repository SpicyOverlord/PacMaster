import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.observation import Observation
from Pacman_Complete.constants import *


class ShowIsInDanger(IAgent):
    """
    This is a simple agent that allows a human to play the game.
    """
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

    def calculateNextMove(self, obs: Observation):

        DebugHelper.drawDot(obs.getPacmanPosition(), 5, DebugHelper.LIGHTBLUE)


        mapPos = obs.map.createMapPosition(obs.getPacmanPosition())
        DebugHelper.drawDot(mapPos.mapNode1.position, 3, DebugHelper.RED)
        if mapPos.isBetweenMapNodes:
            DebugHelper.drawLine(mapPos.mapNode1.position, mapPos.mapNode2.position, DebugHelper.RED, 1)
            DebugHelper.drawDot(mapPos.mapNode2.position, 3, DebugHelper.RED)

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