from abc import abstractmethod, ABC

from PacMaster.Genetics.WeightContainer import WeightContainer
from PacMaster.utils.observation import Observation


class IAgent(ABC):
    @abstractmethod
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        self.gameController = gameController
        self.actionsTaken = 0
        self.pelletsEatenThisLevel = 0

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        raise Exception("NotImplementedException")
    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        raise Exception("NotImplementedException")

    def calculateNextMove(self):
        raise Exception("NotImplementedException")

    def takeStats(self, obs: Observation):
        self.actionsTaken += 1
        self.pelletsEatenThisLevel = obs.getPelletsEaten()
        pass
