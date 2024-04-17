from collections import deque

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Qlearning.GameState import GameState
from PacmanAgentBuilder.Utils.Map import MapPosition
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class OneValueAgent(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

        self.no = 0
        self.yes = 0
        self.lastGameState = None

    def calculateNextMove(self, obs: Observation):
        gameState = GameState(obs, STOP, self.weightContainer)
        if self.lastGameState is None or gameState.equal(self.lastGameState):
            print("SKIPPING")
        else:
            print(gameState.pacmanPos, self.lastGameState.pacmanPos)

            gameStateScore = gameState.calculateGameStateScore(self.lastGameState)
            correct = gameStateScore > 0

            if correct:
                self.yes += 1
            else:
                self.no += 1

            self.lastGameState = gameState

        if self.lastGameState is None:
            self.lastGameState = gameState

        return STOP

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        """
        :return: The best known weight container for this agent
        """
        return WeightContainer({
            'pelletDistanceDecline': 2,
            'pelletDistanceScore': 1,
            'eatPelletScore': 10,
            'tooCloseThreshold': 1,
            'tooCloseValue': 1,
            'ghostDistanceThreshold': 1,
            'ghostDistanceScore': 1,
            'nearestGhostDistanceThreshold': 1,
            'nearestGhostDistanceScore': 1,
            'nextLevelScore': 1,
        })

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        """
        :return: The default weight container for this agent (used in the genetic algorithm to create start population)
        """
        return WeightContainer({
            'pelletDistanceDecline': 1,
            'pelletDistanceScore': 1,
            'eatPelletScore': 1,
            'tooCloseThreshold': 1,
            'tooCloseValue': 1,
            'ghostDistanceThreshold': 1,
            'ghostDistanceScore': 1,
            'nearestGhostDistanceThreshold': 1,
            'nearestGhostDistanceScore': 1,
            'nextLevelScore': 1,
        })
