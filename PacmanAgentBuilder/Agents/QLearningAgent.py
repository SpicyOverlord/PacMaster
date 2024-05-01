from collections import deque
from time import sleep

import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacmanAgentBuilder.Agents.Other.IQagent import IQAgent
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Qlearning.GameState import GameState
from PacmanAgentBuilder.Qlearning.QValueStore import QValueStore, UNKNOWN_POSITION
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class QLearningAgent(IQAgent):

    def __init__(self, gameController, weightContainer: WeightContainer = None, store: QValueStore = None):
        super().__init__(gameController, weightContainer=weightContainer, store=store)

    def calculateNextMove(self, obs: Observation):
        # only make move when pacman is on a node, not between nodes
        mapPos = obs.map.createMapPosition(obs.getPacmanPosition())
        if mapPos.isBetweenMapNodes:
            return STOP

        newState = GameState(obs, weights=self.weightContainer)

        move = self.QLearning(obs, newState)

        # supervised learning (human input)
        # key_pressed = pygame.key.get_pressed()
        # if key_pressed[K_UP]:
        #     move = UP
        # elif key_pressed[K_DOWN]:
        #     move = DOWN
        # elif key_pressed[K_LEFT]:
        #     move = LEFT
        # elif key_pressed[K_RIGHT]:
        #     move = RIGHT

        # update game state with made move
        newState.setMadeMove(move)
        self.lastGameState = newState

        return move

    def QLearning(self, obs: Observation, newState: GameState):
        newStateHash = newState.getHash()
        reward = 0

        # Update the Q value of the last state
        if self.lastGameState is not None:
            lastStateHash = self.lastGameState.getHash()
            reward = newState.calculateReward(self.lastGameState)
            lastMoveIndex = directionToIndex(self.lastGameState.moveMade)

            newReward = self.store.updateQValue(lastStateHash, lastMoveIndex, newStateHash, reward)

            # save reward for later analysis
            self.rewards.append(newReward)

        # moving rho is setting rho based on how many times the agent has seen that position.
        # the more time it has encountered a position, the less likely it is to explore
        # movingRho = max(self.store.baseRho - self.store.getVisitedCount(newStateHash) * (self.store.baseRho * (1 / 200)),0.0)
        movingRho = 0

        if random.random() < movingRho:
            move = self.getRandomMove(obs)
            return move
        else:
            qValues = self.store.getQValues(newStateHash)
            maxQValue = max(qValues)

            if maxQValue == UNKNOWN_POSITION:
                unknownMoves = []
                for i in range(4):
                    if qValues[i] == UNKNOWN_POSITION:
                        unknownMoves.append(i)
                moveIndex = random.choice(unknownMoves)
            else:
                moveIndex = qValues.index(maxQValue)

            move = indexToDirection(moveIndex)
            return move

    def getRandomMove(self, obs: Observation):
        legalMoves = obs.getLegalMoves()
        return random.choice(legalMoves)

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        """
        :return: The best known weight container for this agent
        """
        return WeightContainer({
            'nearestGhostDistanceThreshold': 135.75935,
            'ghostDistanceThreshold': 153.01581,
            'tooCloseThreshold': 243.65984,
            'basePenalty': 9.12306,
            'pelletDistanceDecline': 0.01093,
            'pelletDistanceReward': 34.41305,
            'pelletDistancePenalty': 34.41305,
            'eatPelletReward': 239.7079,
            'tooCloseValue': 7.61317,
            'ghostDistancePenalty': 6.98339,
            'nearestGhostDistancePenalty': 0.01724,
        })

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        """
        :return: The default weight container for this agent (used in the genetic algorithm to create start population)
        """
        return WeightContainer({
            'nearestGhostDistanceThreshold': 1000,
            'ghostDistanceThreshold': 1000,
            'tooCloseThreshold': 1000,
            'basePenalty': 10,
            'pelletDistanceDecline': 1,
            'pelletDistanceReward': 20,
            'pelletDistancePenalty': 20,
            'eatPelletReward': 100,
            'tooCloseValue': 5,
            'ghostDistancePenalty': 5,
            'nearestGhostDistancePenalty': 5,
        })
