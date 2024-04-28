from collections import deque

from PacmanAgentBuilder.Agents.Other.IQagent import IQAgent
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Qlearning.GameState import GameState
from PacmanAgentBuilder.Qlearning.QValueStore import QValueStore
from PacmanAgentBuilder.Utils.Map import MapPosition
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class QLearningAgent(IQAgent):

    def __init__(self, gameController, weightContainer: WeightContainer = None, store: QValueStore = None):
        super().__init__(gameController, weightContainer=weightContainer, store=store)

    def calculateNextMove(self, obs: Observation):
        newState = GameState(obs, weights=self.weightContainer)

        if self.lastGameState is not None:
            if newState.equal(self.lastGameState):
                return self.lastGameState.moveMade

        move = self.QLearning(obs, newState)
        newState.setMadeMove(move)

        self.lastGameState = newState

        # if move == 3:
        #     print("WTF")
        return move

    def QLearning(self, obs: Observation, newState: GameState):
        newStateHash = newState.getHash()
        reward = 0

        # Update the Q value of the last state
        if self.lastGameState is not None:
            lastStateHash = self.lastGameState.getHash()
            reward = newState.calculateReward(self.lastGameState)
            lastMoveIndex = directionToIndex(self.lastGameState.moveMade)

            lastQValue = self.store.getStateQValue(lastStateHash, lastMoveIndex)
            newStateMaxQValue = self.store.getMaxStateQValue(newStateHash)

            newReward = (1 - self.store.alpha) * lastQValue + self.store.alpha * (
                    reward + self.store.gamma * newStateMaxQValue)
            self.store.updateQValue(lastStateHash, lastMoveIndex, newReward)

        # save reward for later analysis
        self.rewards.append(reward)

        # Get the next move
        if random.random() < self.store.rho:
            move = self.getRandomMove(obs)
            # if move == 3:
            #     print("wft")
            return move
        else:
            moveIndex = self.store.getBestAction(newStateHash)
            move = indexToDirection(moveIndex)
            # if move == 3:
            #     print("wft")
            return indexToDirection(moveIndex)

    def getRandomMove(self, obs: Observation):
        legalMoves = obs.getLegalMoves()
        return random.choice(legalMoves)

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        """
        :return: The best known weight container for this agent
        """
        return WeightContainer({
            'nearestGhostDistanceThreshold': 200,
            'ghostDistanceThreshold': 100,
            'tooCloseThreshold': 200,
            'basePenalty': 0.1*10,
            'pelletDistanceDecline': 1*10,
            'pelletDistanceReward': 2*10,
            'eatPelletReward': 5*10,
            'tooCloseValue': 1*10,
            'ghostDistancePenalty': 3*10,
            'nearestGhostDistancePenalty': 5*10,
            'nextLevelReward': 50*10,
            'deathPenalty': 50*10,
        })

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        """
        :return: The default weight container for this agent (used in the genetic algorithm to create start population)
        """
        return WeightContainer({
            'basePenalty': 1,
            'pelletDistanceDecline': 10,
            'pelletDistanceReward': 20,
            'eatPelletReward': 50,
            'tooCloseThreshold': 200,
            'tooCloseValue': 10,
            'ghostDistanceThreshold': 10,
            'ghostDistancePenalty': 30,
            'nearestGhostDistanceThreshold': 200,
            'nearestGhostDistancePenalty': 50,
            'nextLevelReward': 50,
            'deathPenalty': 50,
        })
