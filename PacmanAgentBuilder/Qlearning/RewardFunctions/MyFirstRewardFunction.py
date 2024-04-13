from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Qlearning.RewardFunctions.IRewardFunction import IRewardFunction
from PacmanAgentBuilder.Utils.utils import *


class MyFirstRewardFunction(IRewardFunction):
    def __init__(self, weightContainer: WeightContainer = None):
        super().__init__(weightContainer=weightContainer)

    def calculateReward(self, snapshotList: List[int]) -> float:

        return 1.0

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        """
        :return: The best known weight container for this agent
        """
        return WeightContainer({
            'fleeThreshold': 10.3649,
            'pelletLevelDistance': 171.04447,
            'tooCloseThreshold': 0.55431,
            'tooCloseValue': 2.22647,
            'tooFarAwayThreshold': 0.00324,
            'dangerZoneMultiplier': 0.054,
            'dangerZoneMiddleMapNodeMultiplier': 0.00022,
            'ghostIsCloserMultiplier': 0.00322,
            'edgeMultiplier': 1.49241,
            'pelletLevelDistanceInDangerLevel': 619.93584,
            'pelletsInDangerLevelMultiplier': 0.18195,
            'distanceToPacManMultiplier': 0.0,
            'PelletIslandDistance': 0.0,
            'IslandSizeMultiplier': 9.89987,
            'IslandDistanceMultiplier': 1501.86886,
            'ghostMultiplier': 0.00022,
            'blinky': 0.00017,
            'pinky': 0.18026,
            'inky': 1e-05,
            'clyde': 0.0222
        })

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        """
        :return: The default weight container for this agent (used in the genetic algorithm to create start population)
        """
        return WeightContainer({
            'fleeThreshold': 5,
            'pelletLevelDistance': 100,
            'tooCloseThreshold': 300,
            'tooCloseValue': 100,
            'tooFarAwayThreshold': 1000,
            'dangerZoneMultiplier': 2,
            'dangerZoneMiddleMapNodeMultiplier': 2,
            'ghostIsCloserMultiplier': 2,
            'edgeMultiplier': 2,

            'pelletLevelDistanceInDangerLevel': 60,
            'pelletsInDangerLevelMultiplier': 2,
            'distanceToPacManMultiplier': 2,

            'PelletIslandDistance': 60,
            'IslandSizeMultiplier': 10,
            'IslandDistanceMultiplier': 100,

            'ghostMultiplier': 2,
            'blinky': 2,
            'pinky': 2,
            'inky': 2,
            'clyde': 2
        })
