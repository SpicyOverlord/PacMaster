from collections import deque

from PacmanAgentBuilder.Agents.Other.IQagent import IQAgent
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Qlearning.QValueStore import QValueStore
from PacmanAgentBuilder.Utils.GameStats import GameStats
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from Pacman_Complete.run import GameController


def runGameWithAgent(agentClass: type[IQAgent], weightContainer: WeightContainer = None,
                     store: QValueStore = None,
                     gameSpeed=3, startLives=3, startLevel: int = 0,
                     ghostsEnabled: bool = True, freightEnabled: bool = True, lockDeltaTime=False
                     , disableVisuals=False) -> (GameStats, QValueStore, list[int]):
    """
        Runs a single game with the specified agent.

        :param agentClass: Specify the agent to be evaluated.
        :param gameSpeed: Sets the speed of the game from 0.1 (slow) to 15 (fast). Note: For a higher speed, enable lockDeltaTime.
        :param startLives: The number of lives the agent starts with.
        :param startLevel: Choose the starting level for the agent (0 for level one, 1 for level two, and so on).
        :param ghostsEnabled: Toggle ghosts on or off.
        :param freightEnabled: Toggle if the effect of power pellets should be ignored (ghosts turning blue and stops chasing).
        :param lockDeltaTime: When enabled, the game will run at the highest possible speed regardless of the gameSpeed setting. This provides a stable test environment as the game speed is bottlenecked by your hardware, and can therefore not go faster than your hardware can handle.
        :return: GameStats object containing the statistics of the game.
    """

    if gameSpeed < 0.1 or 15 < gameSpeed:
        raise ValueError(f"gameSpeed ({gameSpeed}) must be between 0.1 and 15 (inclusive). Otherwise the game breaks.")

    game = GameController(gameSpeed=gameSpeed, startLives=startLives,
                          startLevel=startLevel, ghostsEnabled=ghostsEnabled, freightEnabled=freightEnabled,
                          lockDeltaTime=lockDeltaTime, disableVisuals=disableVisuals)
    agent = agentClass(gameController=game, weightContainer=weightContainer, store=store)
    game.startGame(agent=agent)
    while True:
        game.update()
        if game.gameOver:
            # qlearning last move update (death)
            # lastState = agent.lastGameState
            # lastStateHash = lastState.getHash()
            # agent.store.setQValue(
            #     lastStateHash,
            #     lastState.moveMade,
            #     -100
            # )

            # print(agent.newPositionCount)

            gameStats = GameStats(game, agent)

            return gameStats, store, agent.rewards


def calculatePerformanceOverXGames(agentClass: type[IQAgent], weightContainer: WeightContainer = None,
                                   saveInterval: int = 10000,
                                   gameCount: int = 50, gameSpeed=1, startLevel: int = 0, startLives=1,
                                   ghostsEnabled: bool = True, freightEnabled: bool = True,
                                   logging=False, lockDeltaTime=False,
                                   disableVisuals: bool = False) -> float:
    """
        Calculates the performance of the specified agent over a number of games.

        :param agentClass: Specify the agent to be evaluated.
        :param weightContainer: The container with all the weights/variables for the agent.
        :param gameCount: Number of games the agent will play.
        :param gameSpeed: Sets the speed of the game from 0.1 (slow) to 5 (fast). Note: For a higher speed, enable lockDeltaTime.
        :param startLevel: Choose the starting level for the agent (0 for level one, 1 for level two, and so on).
        :param startLives: Choose the number of lives the agent will start with.
        :param ghostsEnabled: Toggle ghosts on or off.
        :param freightEnabled: Toggle if the effect of power pellets should be ignored (ghosts turning blue and stops chasing).
        :param lockDeltaTime: When enabled, the game will run at the highest possible speed regardless of the gameSpeed setting. This provides a stable test environment as the game speed is bottlenecked by your hardware, and can therefore not go faster than your hardware can handle.
        :param logging: Toggle the logging of game-related information to the console while the agent is playing.
        :return: Performance object containing the performance of the agent over the specified number of games.
        """
    if lockDeltaTime:
        DebugHelper.disable()

    constStore = QValueStore()
    print("\nLoading the QTable takes around 1 min.\n"
          "The game will be pause when it is finished. Click space to start the agent.\n")
    constStore.loadQValuesFromBinary("QLearningData/QValues.bin", fullPath=True, verbose=True)
    print("\n--- PRESS SPACE TO START THE AGENT ---\n")

    rewardsMoving: deque[int] = deque(maxlen=5000)
    rewardAverages = []
    gameStats = []
    for i in range(gameCount):
        gameStat, store, rewards = runGameWithAgent(agentClass, weightContainer=weightContainer, store=constStore,
                                                    gameSpeed=gameSpeed,
                                                    startLives=startLives, startLevel=startLevel,
                                                    ghostsEnabled=ghostsEnabled, freightEnabled=freightEnabled,
                                                    lockDeltaTime=lockDeltaTime, disableVisuals=disableVisuals)
        gameStats.append(gameStat)
        constStore = store

        for reward in rewards:
            rewardsMoving.append(reward)
        rewardAverage = sum(rewardsMoving) / len(rewardsMoving) if len(rewardsMoving) > 0 else 0
        rewardAverages.append(rewardAverage)

        if (i + 1) % saveInterval == 0 and not constStore.locked:
            performance = GameStats.calculatePerformance(gameStats[-100:])
            constStore.saveQValuesToBinary(f"QLearningData/qvalues({round(performance['combinedScore'], 3)}).bin",
                                           fullPath=True, verbose=False)

        if logging:
            performance = GameStats.calculatePerformance(gameStats[-100:])
            gameRewardAverage = sum(rewards) / len(rewards) if len(rewards) > 0 else 0
            print(
                f"Game {i + 1}  SCORE:{performance['averageScore']}   AVG REWARD:{round(gameRewardAverage, 3)}   LVL:{gameStat.levelsCompleted}")

    # performance = GameStats.calculateLearningRate(rewardAverages, gameStats)
    performance = GameStats.calculatePerformance(gameStats)["combinedScore"]

    if logging:
        print(f"performance over {gameCount} games: {round(performance, 3)}")

    return performance
