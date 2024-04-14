from abc import abstractmethod, ABC
from typing import List

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Utils.Map import Map
from PacmanAgentBuilder.Utils.observation import Observation


class IRewardFunction(ABC):
    """
    THis is the interface for the reward function. All reward functions must implement this interface.
    """

    @abstractmethod
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        self.gameController = gameController
        self.map = Map(self, gameController.nodes)

        if weightContainer is None:
            self.weightContainer = self.getBestWeightContainer()
        else:
            self.weightContainer = weightContainer

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        return None

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        return None

    @abstractmethod
    def calculateReward(self, snapshotArray: List[int]) -> float:
        raise Exception("NotImplementedException")
