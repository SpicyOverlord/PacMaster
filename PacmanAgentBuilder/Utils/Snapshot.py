from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import directionToVector
from Pacman_Complete.constants import FREIGHT, SPAWN, UP, DOWN, LEFT, RIGHT
from Pacman_Complete.vector import Vector2


class Snapshot:
    def __init__(self, obs: Observation, moveMade: int):
        self.moveMade = moveMade
        self.pacmanPos = obs.getPacmanPosition()
        self.nearest5PelletPosition = obs.getNearestXPelletPosition(5)
        self.ghostPosArray = [ghost.position for ghost in obs.getGhosts()]
        self.ghostDirectionArray = [ghost.direction for ghost in obs.getGhosts()]
        self.ghostActiveArray = [1 if ghost.mode not in [FREIGHT, SPAWN] else 0 for ghost in obs.getGhosts()]
        self.legalMoves = obs.getLegalMoves()

    @staticmethod
    def getParameterNames() -> list[str]:
        paramNames = ['pacman_x', 'pacman_y',
                      'ghost1_x', 'ghost1_y',
                      'ghost2_x', 'ghost2_y',
                      'ghost3_x', 'ghost3_y',
                      'ghost4_x', 'ghost4_y',
                      'ghost1_direction_x', 'ghost1_direction_y',
                      'ghost2_direction_x', 'ghost2_direction_y',
                      'ghost3_direction_x', 'ghost3_direction_y',
                      'ghost4_direction_x', 'ghost4_direction_y',
                      'ghost1_active', 'ghost2_active', 'ghost3_active', 'ghost4_active',
                      'nearest_pellet1_x', 'nearest_pellet1_y',
                      'nearest_pellet2_x', 'nearest_pellet2_y',
                      'nearest_pellet3_x', 'nearest_pellet3_y',
                      'nearest_pellet4_x', 'nearest_pellet4_y',
                      'nearest_pellet5_x', 'nearest_pellet5_y',
                      'legal_move_up', 'legal_move_down', 'legal_move_left', 'legal_move_right',
                      'made_move_up', 'made_move_down', 'made_move_left', 'made_move_right']

        return paramNames

    def getArray(self):
        snapshot = []

        snapshot.append(int(self.pacmanPos.x))
        snapshot.append(int(self.pacmanPos.y))

        for ghost in self.ghostPosArray:
            snapshot.append(int(ghost.x))
            snapshot.append(int(ghost.y))

        for direction in self.ghostDirectionArray:
            directionVector = directionToVector(direction)

            snapshot.append(int(directionVector.x))
            snapshot.append(int(directionVector.y))

        for active in self.ghostActiveArray:
            snapshot.append(active)

        for position in self.nearest5PelletPosition:
            snapshot.append(int(position.x))
            snapshot.append(int(position.y))

        legalMoveArray = [1 if move in self.legalMoves else 0 for move in [UP, DOWN, LEFT, RIGHT]]
        for move in legalMoveArray:
            snapshot.append(move)

        moveVector = directionToVector(self.moveMade)
        snapshot.append(int(moveVector.x))
        snapshot.append(int(moveVector.y))

        return snapshot
