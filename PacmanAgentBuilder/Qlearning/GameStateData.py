from typing import List

from PacmanAgentBuilder.Qlearning.GameState import GameState
from PacmanAgentBuilder.Utils.utils import directionToVector
from Pacman_Complete.constants import UP, DOWN, LEFT, RIGHT
from Pacman_Complete.vector import Vector2


class GameStateData:

    def __init__(self, gameStateList: List[int]):
        if len(gameStateList) != 31:
            raise Exception("The gameStateList should have 31 elements")

        self.moveDistance = 5

        self.current_level_layout = gameStateList[0]

        self.pacman_x = gameStateList[1]
        self.pacman_y = gameStateList[2]

        self.ghost1_x = gameStateList[3]
        self.ghost1_y = gameStateList[4]
        self.ghost1_direction = gameStateList[5]
        self.ghost2_x = gameStateList[6]
        self.ghost2_y = gameStateList[7]
        self.ghost2_direction = gameStateList[8]
        self.ghost3_x = gameStateList[9]
        self.ghost3_y = gameStateList[10]
        self.ghost3_direction = gameStateList[11]
        self.ghost4_x = gameStateList[12]
        self.ghost4_y = gameStateList[13]
        self.ghost4_direction = gameStateList[14]

        self.nearest_pellet1_x = gameStateList[15]
        self.nearest_pellet1_y = gameStateList[16]
        self.nearest_pellet2_x = gameStateList[17]
        self.nearest_pellet2_y = gameStateList[18]
        self.nearest_pellet3_x = gameStateList[19]
        self.nearest_pellet3_y = gameStateList[20]
        self.nearest_pellet4_x = gameStateList[21]
        self.nearest_pellet4_y = gameStateList[22]
        self.nearest_pellet5_x = gameStateList[23]
        self.nearest_pellet5_y = gameStateList[24]

        self.legal_move_up = gameStateList[25]
        self.legal_move_down = gameStateList[26]
        self.legal_move_left = gameStateList[27]
        self.legal_move_right = gameStateList[28]

        self.game_ended = gameStateList[29]

        self.made_move = gameStateList[30]

    def generatePredictions(self) -> List["GameStateData"]:
        predictions = []
        for legalMove in [self.legal_move_up, self.legal_move_down, self.legal_move_left, self.legal_move_right]:
            if legalMove == 1:
                possibleMove = directionToVector(legalMove)
            else:
                continue

            newPacmanPos = Vector2(
                self.pacman_x + possibleMove.x * self.moveDistance,
                self.pacman_y + possibleMove.y * self.moveDistance
            )

            ghost1MoveVector = directionToVector(self.ghost1_direction)
            newGhost1Pos = Vector2(
                self.ghost1_x + ghost1MoveVector.x * self.moveDistance,
                self.ghost1_y + ghost1MoveVector.y * self.moveDistance
            )

            ghost2MoveVector = directionToVector(self.ghost2_direction)
            newGhost2Pos = Vector2(
                self.ghost2_x + ghost2MoveVector.x * self.moveDistance,
                self.ghost2_y + ghost2MoveVector.y * self.moveDistance
            )

            ghost3MoveVector = directionToVector(self.ghost3_direction)
            newGhost3Pos = Vector2(
                self.ghost3_x + ghost3MoveVector.x * self.moveDistance,
                self.ghost3_y + ghost3MoveVector.y * self.moveDistance
            )

            ghost4MoveVector = directionToVector(self.ghost4_direction)
            newGhost4Pos = Vector2(
                self.ghost4_x + ghost4MoveVector.x * self.moveDistance,
                self.ghost4_y + ghost4MoveVector.y * self.moveDistance
            )

            movePredictionArray = [
                self.current_level_layout,

                newPacmanPos.x,
                newPacmanPos.y,

                newGhost1Pos.x,
                newGhost1Pos.y,
                self.ghost1_direction,
                newGhost2Pos.x,
                newGhost2Pos.y,
                self.ghost2_direction,
                newGhost3Pos.x,
                newGhost3Pos.y,
                self.ghost3_direction,
                newGhost4Pos.x,
                newGhost4Pos.y,
                self.ghost4_direction,

                self.nearest_pellet1_x,
                self.nearest_pellet1_y,
                self.nearest_pellet2_x,
                self.nearest_pellet2_y,
                self.nearest_pellet3_x,
                self.nearest_pellet3_y,
                self.nearest_pellet4_x,
                self.nearest_pellet4_y,
                self.nearest_pellet5_x,
                self.nearest_pellet5_y,

                self.legal_move_up,
                self.legal_move_down,
                self.legal_move_left,
                self.legal_move_right,

                self.game_ended,

                self.made_move
            ]

            predictions.append(GameStateData(movePredictionArray))
        return predictions
