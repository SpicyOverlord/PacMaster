from abc import abstractmethod, ABC

from PacMaster.observation import Observation


class IAgent(ABC):
    @abstractmethod
    def __init__(self, gameController):
        self.gameController = gameController
        self.actionsTaken = 0
        self.ghostDistanceSum = 0
        self.dangerLevelSum = 0

    @abstractmethod
    def calculateNextMove(self):
        raise Exception("NotImplementedException")

    def takeStats(self, obs: Observation):
        self.actionsTaken += 1
        self.dangerLevelSum += obs.CalculateDangerLevel()
        pass

