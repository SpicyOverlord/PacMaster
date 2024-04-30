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

        self.startRoute1 = [
            Vector2(240, 520), Vector2(180, 520), Vector2(120, 520), Vector2(120, 580), Vector2(60, 580),
            Vector2(20, 580), Vector2(20, 640), Vector2(240, 640), Vector2(300, 640), Vector2(520, 640),
            Vector2(520, 580), Vector2(480, 580), Vector2(420, 580), Vector2(420, 520), Vector2(360, 520),
            Vector2(300, 520), Vector2(240, 520), Vector2(240, 460), Vector2(180, 460), Vector2(180, 400),
            Vector2(180, 340), Vector2(120, 340), Vector2(120, 220), Vector2(120, 160), Vector2(180, 160),
            Vector2(240, 160), Vector2(300, 160), Vector2(360, 160), Vector2(360, 220), Vector2(300, 220),
            Vector2(300, 280), Vector2(360, 280), Vector2(360, 340), Vector2(420, 340), Vector2(550, 340),
            Vector2(120, 340), Vector2(120, 460), Vector2(180, 460), Vector2(240, 460), Vector2(240, 520),
            Vector2(180, 520), Vector2(180, 580), Vector2(240, 580), Vector2(240, 640), Vector2(300, 640),
            Vector2(300, 580), Vector2(360, 580), Vector2(360, 520), Vector2(300, 520), Vector2(300, 460),
            Vector2(360, 460), Vector2(420, 460), Vector2(420, 340), Vector2(420, 220), Vector2(520, 220),
            Vector2(520, 160), Vector2(420, 160), Vector2(360, 160), Vector2(300, 160), Vector2(240, 160),
            Vector2(180, 160), Vector2(180, 220), Vector2(240, 220), Vector2(240, 280), Vector2(270.0, 280),
            Vector2(300, 280), Vector2(300, 220), Vector2(360, 220), Vector2(360, 160), Vector2(300, 160),
            Vector2(240, 160), Vector2(240, 80), Vector2(120, 80), Vector2(120, 160), Vector2(20, 160),
            Vector2(120, 160),
            Vector2(120, 220), Vector2(120, 340), Vector2(120, 460), Vector2(120, 520), Vector2(180, 520),
            Vector2(240, 520), Vector2(300, 520), Vector2(360, 520), Vector2(420, 520), Vector2(420, 460),
            Vector2(420, 340), Vector2(420, 220), Vector2(420, 160), Vector2(360, 160), Vector2(300, 160),
            Vector2(240, 160), Vector2(180, 160), Vector2(120, 160), Vector2(20, 160), Vector2(20, 220),
            Vector2(120, 220),
            Vector2(120, 160), Vector2(180, 160), Vector2(240, 160), Vector2(300, 160), Vector2(300, 80),
            Vector2(420, 80), Vector2(520, 80), Vector2(520, 160), Vector2(420, 160), Vector2(420, 80),
            Vector2(420, 160), Vector2(420, 220), Vector2(420, 340), Vector2(420, 460), Vector2(520, 460),
            Vector2(520, 520), Vector2(480, 520), Vector2(480, 580), Vector2(420, 580), Vector2(420, 520),
            Vector2(360, 520), Vector2(300, 520), Vector2(240, 520), Vector2(180, 520), Vector2(120, 520),
            Vector2(120, 580), Vector2(60, 580), Vector2(60, 520), Vector2(20, 520), Vector2(20, 460),
            Vector2(120, 460), Vector2(120, 340), Vector2(120, 220), Vector2(20, 220), Vector2(20, 160),
            Vector2(20, 80), Vector2(120, 80), Vector2(240, 80)
        ]
        self.startRoute2 = [
            Vector2(180, 520), Vector2(180, 580), Vector2(120, 580), Vector2(120, 520), Vector2(60, 520),
            Vector2(60, 460), Vector2(120, 460), Vector2(120, 360),

            Vector2(120, 320), Vector2(120, 260), Vector2(80, 260),
            Vector2(80, 200), Vector2(180, 200), Vector2(180, 140), Vector2(180, 80), Vector2(360, 80),
            Vector2(360, 140), Vector2(360, 200), Vector2(460, 200), Vector2(460, 260), Vector2(420, 260),

            Vector2(420, 320), Vector2(420, 360), Vector2(420, 460),
            Vector2(320, 460), Vector2(320, 520), Vector2(360, 520), Vector2(360, 580), Vector2(420, 580),
            Vector2(420, 640), Vector2(300, 640), Vector2(240, 640), Vector2(240, 580), Vector2(180, 580),
            Vector2(180, 520), Vector2(220, 520), Vector2(220, 460), Vector2(120, 460), Vector2(60, 460),
            Vector2(60, 380), Vector2(20, 380), Vector2(20, 320), Vector2(120, 320), Vector2(120, 260),
            Vector2(80, 260), Vector2(80, 200), Vector2(180, 200), Vector2(180, 140), Vector2(240, 140),
            Vector2(240, 220), Vector2(300, 220), Vector2(300, 140), Vector2(360, 140), Vector2(360, 200),
            Vector2(360, 280), Vector2(360, 360), Vector2(420, 360), Vector2(420, 460),

            Vector2(480, 460), Vector2(480, 520), Vector2(420, 520),
            Vector2(480, 520), Vector2(550, 520),
            Vector2(60, 520), Vector2(120, 520), Vector2(120, 580), Vector2(120, 640), Vector2(120, 580),

            Vector2(180, 580), Vector2(240, 580), Vector2(240, 640), Vector2(300, 640), Vector2(300, 580),
            Vector2(360, 580), Vector2(420, 580), Vector2(420, 520), Vector2(480, 520), Vector2(480, 460),
            Vector2(480, 380), Vector2(520, 380), Vector2(520, 320), Vector2(420, 320), Vector2(420, 260),
            Vector2(460, 260), Vector2(520, 260), Vector2(520, 140), Vector2(420, 140), Vector2(360, 140),

            Vector2(360, 80), Vector2(180, 80), Vector2(180, 140),
            Vector2(120, 140), Vector2(20, 140), Vector2(20, 260), Vector2(80, 260), Vector2(120, 260),
            Vector2(120, 320), Vector2(120, 360), Vector2(120, 460), Vector2(60, 460), Vector2(60, 520),
            Vector2(60, 580), Vector2(20, 580), Vector2(20, 640), Vector2(120, 640), Vector2(240, 640),
            Vector2(300, 640), Vector2(420, 640), Vector2(520, 640), Vector2(520, 580), Vector2(480, 580),
            Vector2(480, 520),

        ]

        self.currentRoute = self.startRoute1
        self.currentTarget = 0
        self.pastTarget = Vector2(-999, -999)

        self.currentLevel = 0


    def calculateNextMove(self, obs: Observation):
        # DebugHelper.enable()
        # DebugHelper.drawMap(obs)

        # sleep(0.02)
        mapPos = obs.map.createMapPosition(obs.getPacmanPosition())
        if mapPos.isBetweenMapNodes:
            return STOP
        # print("MOVING")
        # if self.gameController.level >= 15:
        #     return RIGHT

        newState = GameState(obs, weights=self.weightContainer)

        # if self.gameController.level >= 10:
        #     self.lastGameState = newState
        #     return UP

        if obs.gameController.level % 2 != self.currentLevel:
            self.currentLevel = obs.gameController.level % 2
            self.currentTarget = 0
            self.pastTarget = Vector2(-999, -999)

            if self.currentLevel == 0:
                self.currentRoute = self.startRoute1
            else:
                # self.currentTarget = -1
                self.currentRoute = self.startRoute2

        # if self.currentTarget == -1 or self.currentTarget > len(self.currentRoute)-5:
        # sleep(0.2)

        if self.currentTarget != -1:
            dist = manhattanDistance(obs.getPacmanPosition(), self.currentRoute[self.currentTarget])
            if dist <= 10:
                self.currentTarget += 1
                # print(f"new target: {self.startRoute1[self.currentTarget]}")

                if self.currentTarget == len(self.currentRoute) - 1:
                    self.currentTarget = -1
                    # print("finished route")
                    # DebugHelper.pauseGame()

        pacmanTarget = obs.getPacmanTargetPosition()
        if manhattanDistance(obs.getPacmanPosition(), pacmanTarget) <= 5 and pacmanTarget != self.pastTarget:
            if self.currentTarget == -1:
                # print(f"Vector2({pacmanTarget.x}, {pacmanTarget.y}), ", end="")
                self.pastTarget = obs.getPacmanTargetPosition()

        # if self.lastGameState is not None:
        #     if newState.equal(self.lastGameState):
        #         if self.lastGameState.moveMade in obs.getLegalMoves():
        #             pass
        #             # return self.lastGameState.moveMade

        move = self.QLearning(obs, newState)

        # supervised learning (human input)
        # if self.gameController.level < 15:
        #     move = self.getDirection(obs, self.currentRoute[self.currentTarget])

        key_pressed = pygame.key.get_pressed()
        if key_pressed[K_UP]:
            move = UP
        elif key_pressed[K_DOWN]:
            move = DOWN
        elif key_pressed[K_LEFT]:
            move = LEFT
        elif key_pressed[K_RIGHT]:
            move = RIGHT
        # else:
        #     move = STOP

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
        movingRho = max(self.store.baseRho - self.store.getVisitedCount(newStateHash) * (self.store.baseRho * (1 / 1000)),0.0)
        # movingRho = 0
        if random.random() < movingRho:
            move = self.getRandomMove(obs)
            print("RANDOM MOVE")
            return move
        else:
            qValues = self.store.getQValues(newStateHash)
            maxQValue = max(qValues)
            # print(maxQValue)
            if maxQValue == UNKNOWN_POSITION:
                self.newPositionCount += 1
                # return obs.pacman.direction

                unknownMoves = []
                for i in range(4):
                    if qValues[i] == UNKNOWN_POSITION:
                        unknownMoves.append(i)
                # print("RANDOM MOVE")
                moveIndex = random.choice(unknownMoves)
            else:
                # print("KNOWN POSITION!")
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
