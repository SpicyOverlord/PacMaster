from abc import abstractmethod, ABC

from PacMaster.observation import Observation


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

