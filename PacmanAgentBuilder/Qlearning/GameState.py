from typing import List

from PacmanAgentBuilder.Qlearning.GameStateData import GameStateData
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import isInCenterArea
from Pacman_Complete.constants import FREIGHT, SPAWN, UP, DOWN, LEFT, RIGHT, STOP
from Pacman_Complete.vector import Vector2


class GameState:
    simplifyFactor = 1

    def __init__(self, obs: Observation, moveMade: int = STOP):
        self.moveMade = moveMade
        self.pacmanPos = obs.getPacmanPosition()
        self.nearest5PelletPosition = obs.getNearestXPelletPosition(5)
        self.ghostPosArray = [ghost.position for ghost in obs.getGhosts()]
        self.ghostDirectionArray = [ghost.direction for ghost in obs.getGhosts()]
        self.ghostActiveArray = [0 if ghost.mode.current in [FREIGHT, SPAWN] or isInCenterArea(ghost.position) else 1
                                 for ghost in obs.getGhosts()]
        self.legalMoves = obs.getLegalMoves()
        self.currentLevel = obs.currentLevel
        self.gameEnded = 0

    def setGameEnded(self):
        self.gameEnded = 1

    def getInputArray(self) -> List[int]:
        return self.getArray()[:-1]

    def getArray(self) -> List[int]:
        gameState = []

        gameState.append(self.currentLevel % 2)

        simplePacmanPos = GameState.simplifyVector(self.pacmanPos)
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
            simpleGhostPos = GameState.simplifyVector(ghostPos)
            gameState.append(simpleGhostPos.x)
            gameState.append(simpleGhostPos.y)

            ghostDirection = sortedGhostDirectionArray[i]
            gameState.append(ghostDirection)

        for position in self.nearest5PelletPosition:
            simpleNearestPelletPos = GameState.simplifyVector(position)
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

    @staticmethod
    def directionToVector(direction: int) -> Vector2:
        """
        Converts a direction to a vector
        :param direction: The direction
        :return: The vector
        """
        if direction == UP:
            return Vector2(0, -1)
        if direction == DOWN:
            return Vector2(0, 1)
        if direction == LEFT:
            return Vector2(-1, 0)
        if direction == RIGHT:
            return Vector2(1, 0)
        if direction == STOP:
            return Vector2(0, 0)

        raise Exception(f"Direction '{direction}' not recognized")

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
