from abc import abstractmethod, ABC

from PacMaster.observation import Observation


class IAgent(ABC):
    @abstractmethod
    def __init__(self, gameController):
        self.gameController = gameController

    @abstractmethod
    def calculateNextMove(self):
        raise Exception("NotImplementedException")
