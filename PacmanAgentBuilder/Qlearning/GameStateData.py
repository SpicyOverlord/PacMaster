from typing import List


class GameStateData:
    def __init__(self, gameStateList: List[int]):
        if len(gameStateList) != 31:
            raise Exception("The gameStateList should have 31 elements")

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

        self.nearest_pelle1_x = gameStateList[15]
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

