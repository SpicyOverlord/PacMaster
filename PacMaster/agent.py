from PacMaster.observation import Observation
from Pacman_Complete.constants import STOP, CHASE


def calculateNextMove(game):
    obs = Observation(game)

    print(obs.getGhostModeAsStr())

    return STOP
