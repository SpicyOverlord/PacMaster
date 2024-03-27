import os

from PacmanAgentBuilder.Agents.FinalAgent import FinalAgent
from PacmanAgentBuilder.Agents.Other.ShowCollect import ShowCollect
from PacmanAgentBuilder.Agents.Other.ShowDangerLevels import ShowDangerLevels
from PacmanAgentBuilder.Agents.Other.ShowDangerZone import ShowDangerZone
from PacmanAgentBuilder.Agents.Other.ShowGraph import ShowGraph
from PacmanAgentBuilder.Agents.Other.ShowIsInDanger import ShowIsInDanger
from PacmanAgentBuilder.Agents.Other.ShowPathfinding import ShowPathfinding
from PacmanAgentBuilder.Agents.Other.ShowFlee import ShowFlee
from PacmanAgentBuilder.Utils.runnerFunctions import *

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

if __name__ == "__main__":
    # comment the line below to enable the debug helper (show the drawings of the algorithms)
    DebugHelper.disable()

    # --- USED IN THE PRESENTATION ---
    # agentClass = ShowIsInDanger
    # agentClass = ShowDangerLevels
    # agentClass = ShowDangerZone
    # agentClass = ShowGraph
    # agentClass = ShowPathfinding
    # agentClass = ShowFlee
    # agentClass = ShowCollect

    agentClass = FinalAgent

    # this will run the agent in 50 games and print the average performance over the 50 games
    stats = calculatePerformanceOverXGames(
        agentClass=agentClass,  # Specify the agent to be evaluated.
        gameCount=10,  # Number of games the agent will play.
        startLevel=0,  # Choose the starting level for the agent (0 for level one, 1 for level two, and so on).
        startLives=3,  # Choose the number of lives the agent will start with.
        ghostsEnabled=True,  # Toggle ghosts on or off.
        freightEnabled=True,  # Toggle if the effect of power pellets should be ignored.
        logging=True  # Toggle the logging of game-related information to the console while the agent is playing.
    )
    print(f"Score: {stats['maxScore']}\n"
          f"Levels Completed: {stats['maxLevelsCompleted']}\n")
