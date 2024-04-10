import random

import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.observation import Observation
from Pacman_Complete.constants import *


class ShowGraph(IAgent):
    """
    This is a simple agent that allows a human to play the game.
    """
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

    def calculateNextMove(self, obs: Observation):
        # DebugHelper.drawMap(obs)

        for mapNode in obs.map.mapNodes:
            # neighborCount = len(mapNode.neighborContainers)
            # if neighborCount == 1:
            #     DebugHelper.drawDot(mapNode.position, 5, DebugHelper.RED)
            # elif neighborCount == 2:
            #     DebugHelper.drawDot(mapNode.position, 5, DebugHelper.BLUE)
            # elif neighborCount == 3:
            #     DebugHelper.drawDot(mapNode.position, 5, DebugHelper.GREEN)
            # elif neighborCount == 4:
            #     DebugHelper.drawDot(mapNode.position, 5, DebugHelper.PURPLE)
            # else:
            #     DebugHelper.drawDot(mapNode.position, 5 , DebugHelper.YELLOW)

            for direction in [UP, DOWN, LEFT, RIGHT]:
                # if mapNode.node.neighbors[direction] is None:
                #     continue

                neighborContainer = mapNode.getNeighborInDirection(direction)
                if neighborContainer is not None and mapNode.position == neighborContainer.mapNode.position:
                    DebugHelper.drawDot(mapNode.position, 10, DebugHelper.GREEN)

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