from abc import abstractmethod, ABC

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Utils.observation import Observation


class IAgent(ABC):
    """
    THis is the interface for the agent. All Agents must implement this interface.
    """

    @abstractmethod
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        self.gameController = gameController
        self.actionsTaken = 0
        self.pelletsEatenThisLevel = 0
        self.gameStates = []

        if weightContainer is None:
            self.weightContainer = self.getBestWeightContainer()
        else:
            self.weightContainer = weightContainer

        self.yes = 0
        self.no = 0

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        return None

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        return None

    @abstractmethod
    def calculateNextMove(self, obs: Observation):
        raise Exception("NotImplementedException")

    def takeStats(self):
        self.actionsTaken += 1
        self.pelletsEatenThisLevel = self.gameController.pellets.numEaten
        pass
