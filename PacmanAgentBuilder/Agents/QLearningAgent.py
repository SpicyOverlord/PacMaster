from collections import deque
from time import sleep

import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacmanAgentBuilder.Agents.Other.IQagent import IQAgent
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Qlearning.GameState import GameState
from PacmanAgentBuilder.Qlearning.QValueStore import QValueStore, UNKNOWN_POSITION
from PacmanAgentBuilder.Utils.Map import MapPosition
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class QLearningAgent(IQAgent):

    def __init__(self, gameController, weightContainer: WeightContainer = None, store: QValueStore = None):
        super().__init__(gameController, weightContainer=weightContainer, store=store)

        self.startRoute = [
            Vector2(120, 520), Vector2(120, 580), Vector2(20, 580), Vector2(20, 640),
            Vector2(520, 640), Vector2(520, 580), Vector2(420, 580), Vector2(420, 520),
            Vector2(240, 520), Vector2(240, 460), Vector2(180, 460), Vector2(180, 340),
            Vector2(120, 340), Vector2(120, 160), Vector2(360, 160),
            Vector2(360, 220), Vector2(300, 220), Vector2(300, 280),
            Vector2(360, 280), Vector2(360, 400), Vector2(180, 400),
            Vector2(180, 340), Vector2(120, 340), Vector2(120, 340),
            Vector2(120, 460), Vector2(20, 460), Vector2(20, 520),
            Vector2(20, 520),
            Vector2(60, 520),
            Vector2(60, 580),
            Vector2(120, 580),
            Vector2(120, 520),
            Vector2(180, 520),
            Vector2(180, 580),
            Vector2(240, 580),
            Vector2(240, 640),
            Vector2(300, 640),
            Vector2(300, 580),
            Vector2(360, 580),
            Vector2(360, 520),
            Vector2(420, 520),
            Vector2(420, 580),
            Vector2(480, 580),
            Vector2(480, 520),
            Vector2(520, 520),
            Vector2(520, 460),
            Vector2(420, 460),
            Vector2(420, 520),
            Vector2(300, 520),
            Vector2(300, 460),
            Vector2(420, 460),


            Vector2(420, 220),


            Vector2(520, 220),
            Vector2(520, 80),
            Vector2(300, 80),
            Vector2(300, 160),
            Vector2(240, 160),
            Vector2(240, 80),
            Vector2(20, 80),
            Vector2(20, 220),
            Vector2(120, 220),
            Vector2(120, 160),
            Vector2(20, 160),
            Vector2(20, 80),
            Vector2(120, 80),
            Vector2(120, 160),
            Vector2(180, 160),
            Vector2(180, 220),
            Vector2(240, 220),
            Vector2(240, 280),
            Vector2(300, 280),
            Vector2(300, 220),
            Vector2(360, 220),
            Vector2(360, 160),
            Vector2(520, 160),
            Vector2(420, 160),
            Vector2(420, 80),
            Vector2(420, 220),
            # Vector2(,),Vector2(,),
        ]
        self.currentTarget = 0

    def calculateNextMove(self, obs: Observation):
        # sleep(0.01)
        # DebugHelper.enable()
        # DebugHelper.drawMap(obs)
        newState = GameState(obs, weights=self.weightContainer)

        if self.currentTarget != -1:
            dist = manhattanDistance(obs.getPacmanPosition(), self.startRoute[self.currentTarget])
            if dist <= 10:
                self.currentTarget += 1
                # print(f"new target: {self.startRoute[self.currentTarget]}")

                if self.currentTarget == len(self.startRoute) - 1:
                    self.currentTarget = -1
                    # print("finished route")
                    # DebugHelper.pauseGame()

        # if self.lastGameState is not None:
        #     if newState.equal(self.lastGameState):
        #         if self.lastGameState.moveMade in obs.getLegalMoves():
        #             pass
        #             # return self.lastGameState.moveMade

        move = self.QLearning(obs, newState)

        # supervised learning (human input)
        # DebugHelper.drawDot(self.startRoute[self.currentTarget], 3, DebugHelper.RED)
        move = self.getDirection(obs, self.startRoute[self.currentTarget])

        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            move = UP
        if key_pressed[K_DOWN]:
            move = DOWN
        if key_pressed[K_LEFT]:
            move = LEFT
        if key_pressed[K_RIGHT]:
            move = RIGHT

        newState.setMadeMove(move)
        self.lastGameState = newState

        # if move == 3:
        #     print("WTF")
        return move

    def getDirection(self, obs: Observation, vector: Vector2) -> int:
        """
        Get the direction from pacman to a vector
        :param obs: The current observation
        :param vector: The vector to get the direction to
        :return: The direction to the vector
        """
        pacmanPosition = obs.getPacmanPosition()
        if pacmanPosition.y == vector.y:
            if pacmanPosition.x < vector.x:
                return RIGHT
            else:
                return LEFT
        else:
            if pacmanPosition.y < vector.y:
                return DOWN
            else:
                return UP

    def QLearning(self, obs: Observation, newState: GameState):
        newStateHash = newState.getHash()
        reward = 0

        # Update the Q value of the last state
        if self.lastGameState is not None:
            lastStateHash = self.lastGameState.getHash()
            reward = newState.calculateReward(self.lastGameState)
            lastMoveIndex = directionToIndex(self.lastGameState.moveMade)

            # lastQValue = self.store.getStateQValue(lastStateHash, lastMoveIndex)
            # newStateMaxQValue = self.store.getMaxStateQValue(newStateHash)

            newReward = self.store.updateQValue(lastStateHash, lastMoveIndex, newStateHash, reward)

            # save reward for later analysis
            self.rewards.append(newReward)

        # Get the next move
        if random.random() < self.store.rho:
            move = self.getRandomMove(obs)
            return move
        else:
            qValues = self.store.getQValues(newStateHash)
            maxQValue = max(qValues)
            if maxQValue == UNKNOWN_POSITION:
                # print("UNKNOWN POSITION!")
                unknownMoves = []
                for i in range(4):
                    if qValues[i] == UNKNOWN_POSITION:
                        unknownMoves.append(i)
                moveIndex = random.choice(unknownMoves)
            else:
                moveIndex = qValues.index(maxQValue)
                # print(f"known position! ({maxQValue}  ,  {moveIndex})")

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
            'nearestGhostDistanceThreshold': 4.46521,
            'ghostDistanceThreshold': 0.6382,
            'tooCloseThreshold': 1361.46979,
            'basePenalty': 0.1,
            'pelletDistanceDecline': 3.46962,
            'pelletDistanceReward': 22.61115,
            'eatPelletReward': 68.21019,
            'tooCloseValue': 67.01752,
            'ghostDistancePenalty': 6.06404,
            'nearestGhostDistancePenalty': 3.5819,
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
            'tooCloseThreshold': 1000,
            'tooCloseValue': 10,
            'ghostDistanceThreshold': 10,
            'ghostDistancePenalty': 30,
            'nearestGhostDistanceThreshold': 200,
            'nearestGhostDistancePenalty': 50,
        })
