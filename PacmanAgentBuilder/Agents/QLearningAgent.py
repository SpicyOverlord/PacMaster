from collections import deque

from Data.DataSetJoiner import simplifyVector
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Qlearning.GameState import GameState
from PacmanAgentBuilder.Qlearning.QValueStore import QValueStore
from PacmanAgentBuilder.Utils.Map import MapPosition
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class QLearningAgent(IAgent):
    rewards: deque = deque(maxlen=20000)

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

        if move == 3:
            print("WTF")
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




        QLearningAgent.rewards.append(reward)
        if self.actionsTaken == 1:
            print(f"{round(sum(QLearningAgent.rewards) / len(self.rewards),3)}")



        # Get the next move
        if random.random() < self.store.rho:
            move = self.getRandomMove(obs)
            if move == 3:
                print("wft")
            return move
        else:
            moveIndex = self.store.getBestAction(newStateHash)
            move = indexToDirection(moveIndex)
            if move == 3:
                print("wft")
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
            'basePenalty': 1,
            'pelletDistanceDecline': 1,
            'pelletDistanceReward': 2,
            'eatPelletReward': 5,
            'tooCloseThreshold': 200,
            'tooCloseValue': 1,
            'ghostDistanceThreshold': 10,
            'ghostDistancePenalty': 3,
            'nearestGhostDistanceThreshold': 200,
            'nearestGhostDistancePenalty': 5,
            'nextLevelReward': 50,
            'deathPenalty': 50,
        })

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        """
        :return: The default weight container for this agent (used in the genetic algorithm to create start population)
        """
        return None
