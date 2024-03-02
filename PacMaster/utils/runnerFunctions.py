from PacMaster.Genetics.WeightContainer import WeightContainer
from PacMaster.agents.HumanAgent import HumanAgent
from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.gamestats import GameStats
from Pacman_Complete.run import GameController


def runGameWithHuman(gameSpeed=1, startLives=3) -> int:
    game = GameController(gameSpeed=gameSpeed, startLives=startLives, isHumanPlayer=True)
    agent = HumanAgent(gameController=game)
    game.startGame(agent=agent)
    while True:
        game.update()
        if game.gameOver:
            print("Actions taken:", agent.actionsTaken)
            print("score:", game.score)
            print("levels completed:", game.level)
            return game.score


def runGameWithAgent(agentType: type[IAgent], weightContainer: WeightContainer = None,
                     gameSpeed=3, startLives=3, startLevel: int = 0,
                     ghostsEnabled: bool = True, freightEnabled: bool = True, lockFrameRate=False) -> GameStats:
    if gameSpeed < 0.1 or 15 < gameSpeed:
        raise ValueError(f"gameSpeed ({gameSpeed}) must be between 0.1 and 10 (inclusive). Otherwise the game breaks.")

    game = GameController(gameSpeed=gameSpeed, startLives=startLives, isHumanPlayer=False,
                          startLevel=startLevel, ghostsEnabled=ghostsEnabled, freightEnabled=freightEnabled,
                          lockFrameRate=lockFrameRate)
    agent = agentType(gameController=game, weightContainer=weightContainer)
    game.startGame(agent=agent)
    while True:
        game.update()
        if game.gameOver:
            return GameStats(game, agent)


def calculatePerformanceOverXGames(agentClass: type[IAgent], weightContainer: WeightContainer = None,
                                   gameCount: int = 20, gameSpeed=5, startLevel: int = 0, startLives=1,
                                   ghostsEnabled: bool = True, freightEnabled: bool = True,
                                   logging=False, lockFrameRate=False):
    gameStats = []
    for i in range(gameCount):
        if logging:
            print(f"Running game {i + 1}...")

        gameStats.append(runGameWithAgent(agentClass, weightContainer=weightContainer, gameSpeed=gameSpeed,
                                          startLives=startLives, startLevel=startLevel,
                                          ghostsEnabled=ghostsEnabled, freightEnabled=freightEnabled,
                                          lockFrameRate=lockFrameRate))

        if logging:
            print(f"Game {i + 1} result: {gameStats[i]}")

    performance = GameStats.calculateCombinedRating(gameStats)

    if logging:
        print(f"Performance over {gameCount} games: {performance}")

    return performance
