from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.HumanAgent import HumanAgent
from PacmanAgentBuilder.Agents.Iagent import IAgent
from PacmanAgentBuilder.Utils.GameStats import GameStats
from Pacman_Complete.run import GameController


def runGameWithAgent(agentClass: type[IAgent], weightContainer: WeightContainer = None,
                     gameSpeed=3, startLives=3, startLevel: int = 0,
                     ghostsEnabled: bool = True, freightEnabled: bool = True, lockDeltaTime=False) -> GameStats:
    if gameSpeed < 0.1 or 15 < gameSpeed:
        raise ValueError(f"gameSpeed ({gameSpeed}) must be between 0.1 and 15 (inclusive). Otherwise the game breaks.")

    game = GameController(gameSpeed=gameSpeed, startLives=startLives,
                          startLevel=startLevel, ghostsEnabled=ghostsEnabled, freightEnabled=freightEnabled,
                          lockDeltaTime=lockDeltaTime)
    agent = agentClass(gameController=game, weightContainer=weightContainer)
    game.startGame(agent=agent)
    while True:
        game.update()
        if game.gameOver:
            return GameStats(game, agent)


def calculatePerformanceOverXGames(agentClass: type[IAgent], weightContainer: WeightContainer = None,
                                   gameCount: int = 50, gameSpeed=1, startLevel: int = 0, startLives=1,
                                   ghostsEnabled: bool = True, freightEnabled: bool = True,
                                   logging=False, lockDeltaTime=False):
    gameStats = []
    for i in range(gameCount):
        if logging:
            print(f"Running game {i + 1}...")

        gameStats.append(runGameWithAgent(agentClass, weightContainer=weightContainer, gameSpeed=gameSpeed,
                                          startLives=startLives, startLevel=startLevel,
                                          ghostsEnabled=ghostsEnabled, freightEnabled=freightEnabled,
                                          lockDeltaTime=lockDeltaTime))

        if logging:
            print(f"Game {i + 1} result: {gameStats[i]}")

    performance = GameStats.calculatePerformance(gameStats)

    if logging:
        print(f"Performance over {gameCount} games: {performance}")

    return performance
