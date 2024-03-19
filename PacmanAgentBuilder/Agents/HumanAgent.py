import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacmanAgentBuilder.Agents.Iagent import IAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.observation import Observation
from Pacman_Complete.constants import *


class HumanAgent(IAgent):
    """
    This is a simple agent that allows a human to play the game.
    """
    def __init__(self, gameController):
        super().__init__(gameController)

    def calculateNextMove(self, obs: Observation):
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