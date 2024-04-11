from typing import List

from PacmanAgentBuilder.Utils.utils import isInCenterArea
from Pacman_Complete.constants import FREIGHT, SPAWN, UP, DOWN, LEFT, RIGHT, STOP
from Pacman_Complete.vector import Vector2


class Snapshot:
    def __init__(self, obs, moveMade: int = STOP):
        self.moveMade = moveMade
        self.pacmanPos = obs.getPacmanPosition()
        self.nearest5PelletPosition = obs.getNearestXPelletPosition(5)
        self.ghostPosArray = [ghost.position for ghost in obs.getGhosts()]
        self.ghostDirectionArray = [ghost.direction for ghost in obs.getGhosts()]
        self.ghostActiveArray = [0 if ghost.mode.current in [FREIGHT, SPAWN] or isInCenterArea(ghost.position) else 1 for ghost in obs.getGhosts()]
        self.legalMoves = obs.getLegalMoves()
        self.currentLevel = obs.currentLevel
        self.gameEnded = 0

    def setGameEnded(self):
        self.gameEnded = 1

    def getInputArray(self) -> List[int]:
        return self.getArray()[:-4]

    def getArray(self) -> List[int]:
        snapshot = []

        snapshot.append(self.currentLevel % 2)

        snapshot.append(int(self.pacmanPos.x))
        snapshot.append(int(self.pacmanPos.y))

        for ghost in self.ghostPosArray:
            snapshot.append(int(ghost.x))
            snapshot.append(int(ghost.y))

        for direction in self.ghostDirectionArray:
            directionVector = self.directionToVector(direction)

            snapshot.append(int(directionVector.x))
            snapshot.append(int(directionVector.y))

        for active in self.ghostActiveArray:
            snapshot.append(active)

        for position in self.nearest5PelletPosition:
            snapshot.append(int(position.x))
            snapshot.append(int(position.y))

        snapshot.append(self.gameEnded)

        legalMoveArray = [1 if move in self.legalMoves else 0 for move in [UP, DOWN, LEFT, RIGHT]]
        for move in legalMoveArray:
            snapshot.append(move)

        madeModeArray = self.directionToArray(self.moveMade)
        for move in madeModeArray:
            snapshot.append(move)

        return snapshot

    def directionToVector(self, direction: int) -> Vector2:
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
