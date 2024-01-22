from typing import Tuple, Dict, Union, Set, Any

from PacMaster.agents.Iagent import IAgent
from PacMaster.gamestats import GameStats
from Pacman_Complete.run import GameController


def runGameWithHuman(gameSpeed=1, startLives=3) -> int:
    game = GameController(gameSpeed=gameSpeed, startLives=startLives, isHumanPlayer=True)
    game.startGame()
    while True:
        game.update()
        if game.gameOver:
            print("Actions taken:", game.actionsTaken)
            print("score:", game.score)
            print("levels completed:", game.level)
            return game.score


def runGameWithAgent(agentType: type[IAgent], gameSpeed=1, startLives=3) -> GameStats:
    game = GameController(gameSpeed=gameSpeed, startLives=startLives, isHumanPlayer=False)
    agent = agentType(gameController=game)
    game.startGame(agent=agent)
    while True:
        game.update()
        if game.gameOver:
            return GameStats(game, agent)


def calculatePerformanceOverXGames(agentClass: type[IAgent], gameCount: int, gameSpeed=5):
    gameStats = []
    for i in range(gameCount):
        gameStats.append(runGameWithAgent(agentClass, gameSpeed=gameSpeed, startLives=1))

    performance = GameStats.calculateCombinedRating(gameStats)
    print(f"Performance over {gameCount} games: {performance}")


