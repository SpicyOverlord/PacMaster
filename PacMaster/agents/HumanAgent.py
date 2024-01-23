import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.observation import Observation
from Pacman_Complete.constants import *


class HumanAgent(IAgent):
    def __init__(self, gameController):
        super().__init__(gameController)

    def calculateNextMove(self):
        obs = Observation(self.gameController)
        self.takeStats(obs)

        # make sure that pacman position is not outside the map
        if not obs.validatePacmanPosition():
            print("Invalid pacman position:", obs.getPacmanPosition())
            return STOP

        if self.actionsTaken % 10 == 0:
            print(obs.getPacmanPosition())

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