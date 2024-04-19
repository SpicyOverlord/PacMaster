import os

from PacmanAgentBuilder.Agents.FinalAgent import FinalAgent
from PacmanAgentBuilder.Agents.FinalAgentWithRewardFunction import FinalAgentWithRewardFunction
from PacmanAgentBuilder.Agents.OneValueAgent import OneValueAgent
from PacmanAgentBuilder.Agents.Other.IslandCollectorAgent import IslandCollectorAgent
from PacmanAgentBuilder.Agents.Other.ShowDangerLevels import ShowDangerLevels
from PacmanAgentBuilder.Agents.Other.ShowDangerZone import ShowDangerZone
from PacmanAgentBuilder.Agents.Other.ShowGraph import ShowGraph
from PacmanAgentBuilder.Agents.Other.ShowIsInDanger import ShowIsInDanger
from PacmanAgentBuilder.Agents.Other.ShowPathfinding import ShowPathfinding
from PacmanAgentBuilder.Agents.Other.ShowFlee import ShowFlee
from PacmanAgentBuilder.Utils.runnerFunctions import *

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

# import tracemalloc


if __name__ == "__main__":
    # tracemalloc.start()

    DebugHelper.enable()
    # --- USED IN THE PRESENTATION ---
    # rewardFunctionClass = ShowIsInDanger
    # rewardFunctionClass = ShowDangerLevels
    # rewardFunctionClass = ShowDangerZone
    # rewardFunctionClass = ShowGraph
    # rewardFunctionClass = ShowPathfinding
    # rewardFunctionClass = ShowFlee
    # rewardFunctionClass = IslandCollectorAgent

    agentClass = FinalAgent
    # agentClass = FinalAgentWithRewardFunction

    # this will run the agent in 50 games and print the average performance over the 50 games
    stats = calculatePerformanceOverXGames(
        agentClass=agentClass,  # Specify the agent to be evaluated.
        gameCount=100,  # Number of games the agent will play.
        gameSpeed=1,  # Sets the speed of the game from 0.1 (slow) to 15 (fast).
        startLevel=0,  # Choose the starting level for the agent (0 for level one, 1 for level two, and so on).
        startLives=10,  # Choose the number of lives the agent will start with.
        ghostsEnabled=True,  # Toggle ghosts on or off.
        freightEnabled=True,  # Toggle if the effect of power pellets should be ignored.
        lockDeltaTime=True,  # When enabled, the game will run at the highest possible speed.
        logging=False,  # Toggle the logging of game-related information to the console while the agent is playing.
        disableVisuals=True  # Toggle the visuals of the game.
    )

    # # Take a snapshot of the current memory allocation
    # snapshot = tracemalloc.take_snapshot()
    #
    # # Get statistics for the top memory blocks
    # top_stats = snapshot.statistics('lineno')
    # for stat in top_stats[:20]:
    #     print(stat)
