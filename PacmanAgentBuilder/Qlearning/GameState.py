from typing import List

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Qlearning.GameStateData import GameStateData
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import isInCenterArea
from Pacman_Complete.constants import FREIGHT, SPAWN, UP, DOWN, LEFT, RIGHT, STOP
from Pacman_Complete.vector import Vector2


class GameState:
    simplifyFactor = 20

    def __init__(self, obs: Observation, moveMade: int = STOP, weights: WeightContainer = None):
        self.moveMade = moveMade
        self.pacmanPos = self.simplifyVector(obs.getPacmanPosition())
        self.nearest5PelletPosition = obs.getNearestXPelletPosition(5)
        self.ghostPosArray = [self.simplifyVector(ghost.position) for ghost in obs.getGhosts()]
        self.ghostDirectionArray = [ghost.direction for ghost in obs.getGhosts()]
        self.ghostActiveArray = [0 if ghost.mode.current in [FREIGHT, SPAWN] or isInCenterArea(ghost.position) else 1
                                 for ghost in obs.getGhosts()]
        self.legalMoves = obs.getLegalMoves()
        self.currentLevel = obs.currentLevel
        self.gameEnded = 0

        if WeightContainer is None:
            return

        self.weightContainer = weights

        #
        # --- extras ---
        #

        self.pelletCount = len(obs.getPelletPositions())

        self.pelletDistanceValue = 0
        for index, pellet in enumerate(self.nearest5PelletPosition):
            distanceWeight = 1 / ((index + 1) / weights.get('pelletDistanceDecline'))
            self.pelletDistanceValue += distanceWeight * obs.map.calculateDistance(pellet, self.pacmanPos)

        self.nearestGhostDistance = 9999
        for ghostPos in self.ghostPosArray:
            if ghostPos.x == 0 and ghostPos.y == 0:
                continue

            distance = obs.map.calculateDistance(ghostPos, self.pacmanPos)
            if distance < self.nearestGhostDistance:
                self.nearestGhostDistance = distance

        minGhostDistance = 9999999
        totalGhostDistance = 0.0
        ghostsDangerValue = 0.0
        numberOfCloseGhosts = 0
        for ghost in obs.getGhosts():
            # ignore ghost if it is not dangerous
            if ghost.mode.current in (FREIGHT, SPAWN) or isInCenterArea(ghost.position):
                continue
            ghostPath, ghostDistance = obs.map.calculateGhostPath(ghost=ghost, endVector=self.pacmanPos)
            # ignore ghost if it can't reach position (this normally only happens if the ghost is in the start area)
            if len(ghostPath) == 0:
                continue
            minGhostDistance = min(minGhostDistance, ghostDistance)
            totalGhostDistance += ghostDistance
            # Threshold distance for a ghost to be considered 'close'
            if ghostDistance < weights.get('tooCloseThreshold'):
                numberOfCloseGhosts += 1
        closestGhostValue = (1 / (minGhostDistance + 1)) * 1000
        closeGhostValue = numberOfCloseGhosts * weights.get('tooCloseValue')
        self.GhostDistanceValue = closestGhostValue + closeGhostValue + ghostsDangerValue

    def equal(self, other: "GameState") -> bool:
        return self.pacmanPos == other.pacmanPos and self.ghostPosArray == other.ghostPosArray

    def calculateGameStateScore(self, lastGameState: "GameState") -> (int, int):
        gameStateScore = 0

        # finished level
        if self.currentLevel > lastGameState.currentLevel:
            gameStateScore += 1 + self.weightContainer.get('nextLevelScore')

        # pellets
        if self.pelletCount < lastGameState.pelletCount:
            gameStateScore += 1 + self.weightContainer.get('eatPelletScore')
        elif self.pelletDistanceValue < lastGameState.pelletDistanceValue:
            gameStateScore += 1 + self.weightContainer.get('pelletDistanceScore')

        # ghosts
        if (self.weightContainer.get(
                'ghostDistanceThreshold') < self.GhostDistanceValue < lastGameState.GhostDistanceValue):
            gameStateScore -= 1 + self.weightContainer.get('ghostDistanceScore')
        if self.weightContainer.get(
                'nearestGhostDistanceThreshold') < self.nearestGhostDistance < lastGameState.nearestGhostDistance:
            gameStateScore -= 1 + self.weightContainer.get('nearestGhostDistanceScore')

        return gameStateScore

    def setGameEnded(self):
        self.gameEnded = 1

    def getInputArray(self) -> List[int]:
        return self.getArray()[:-1]

    def getArray(self) -> List[int]:
        gameState = []

        gameState.append(self.currentLevel % 2)

        simplePacmanPos = self.pacmanPos
        gameState.append(simplePacmanPos.x)
        gameState.append(simplePacmanPos.y)

        # sort Ghosts by position (this makes which ghost is not matter anymore, only the position matters)
        sorted_zipped_lists = sorted(zip(self.ghostPosArray, self.ghostDirectionArray, self.ghostActiveArray),
                                     key=lambda pos_dir: (pos_dir[0].x, pos_dir[0].y))
        sortedGhostPosArray, sortedGhostDirectionArray, sortedGhostActiveArray = zip(*sorted_zipped_lists)

        for i in range(4):
            ghostActive = sortedGhostActiveArray[i]

            if ghostActive == 0:  # if ghost is not active
                gameState.append(0)  # x
                gameState.append(0)  # y
                gameState.append(0)  # dir
                continue

            ghostPos = sortedGhostPosArray[i]
            simpleGhostPos = ghostPos
            gameState.append(simpleGhostPos.x)
            gameState.append(simpleGhostPos.y)

            ghostDirection = sortedGhostDirectionArray[i]
            gameState.append(ghostDirection)

        for position in self.nearest5PelletPosition:
            simpleNearestPelletPos = position
            gameState.append(simpleNearestPelletPos.x)
            gameState.append(simpleNearestPelletPos.y)

        legalMoveArray = [1 if move in self.legalMoves else 0 for move in [UP, DOWN, LEFT, RIGHT]]
        for move in legalMoveArray:
            gameState.append(move)

        # madeModeArray = self.directionToArray(self.moveMade)
        # for move in madeModeArray:
        #     gameState.append(move)

        gameState.append(self.gameEnded)

        gameState.append(self.moveMade)

        return gameState

    def toGameStateData(self) -> GameStateData:
        return GameStateData(self.getArray())

    @staticmethod
    def simplifyVector(vector: Vector2) -> Vector2:
        newX = round(int(vector.x - 19) / GameState.simplifyFactor)
        newY = round(int(vector.y - 79) / GameState.simplifyFactor)

        return Vector2(int(newX), int(newY))

    def directionToArray(self, direction: int) -> List[int]:
        """
        Converts a direction to an array
        :param direction: The direction
        :return: The array
        """
        if direction == UP:
            return [1, 0, 0, 0]
        if direction == DOWN:
            return [0, 1, 0, 0]
        if direction == LEFT:
            return [0, 0, 1, 0]
        if direction == RIGHT:
            return [0, 0, 0, 1]
        if direction == STOP:
            return [0, 0, 0, 0]

        raise Exception(f"Direction '{direction}' not recognized")
