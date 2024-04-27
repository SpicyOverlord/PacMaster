from abc import abstractmethod, ABC

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Qlearning.QValueStore import QValueStore
from PacmanAgentBuilder.Utils.observation import Observation


class IAgent(ABC):
    """
    THis is the interface for the agent. All Agents must implement this interface.
    """

    @abstractmethod
    def __init__(self, gameController, weightContainer: WeightContainer = None, store: QValueStore = None):
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

        if store is not None:
            self.store = QValueStore()
        else:
            self.store = store

        self.lastGameState = None


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
