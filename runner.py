import os

from PacmanAgentBuilder.Agents.FinalAgent import FinalAgent
from PacmanAgentBuilder.Agents.Other.IslandCollectorAgent import IslandCollectorAgent
from PacmanAgentBuilder.Agents.Other.ShowDangerLevels import ShowDangerLevels
from PacmanAgentBuilder.Agents.Other.ShowDangerZone import ShowDangerZone
from PacmanAgentBuilder.Agents.Other.ShowGraph import ShowGraph
from PacmanAgentBuilder.Agents.Other.ShowIsInDanger import ShowIsInDanger
from PacmanAgentBuilder.Agents.Other.ShowPathfinding import ShowPathfinding
from PacmanAgentBuilder.Agents.Other.ShowFlee import ShowFlee
from PacmanAgentBuilder.Utils.runnerFunctions import *

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

if __name__ == "__main__":
    # --- USED IN THE PRESENTATION ---
    # agentClass = ShowIsInDanger
    # agentClass = ShowDangerLevels
    # agentClass = ShowDangerZone
    # agentClass = ShowGraph
    # agentClass = ShowPathfinding
    # agentClass = ShowFlee
    # agentClass = IslandCollectorAgent

    agentClass = FinalAgent

    # this will run the agent in 50 games and print the average performance over the 50 games
    stats = calculatePerformanceOverXGames(
        agentClass=agentClass,  # Specify the agent to be evaluated.
        gameCount=10000,  # Number of games the agent will play.
        gameSpeed=0.7,  # Sets the speed of the game from 0.1 (slow) to 15 (fast).
        startLevel=0,  # Choose the starting level for the agent (0 for level one, 1 for level two, and so on).
        startLives=1,  # Choose the number of lives the agent will start with.
        ghostsEnabled=True,  # Toggle ghosts on or off.
        freightEnabled=True,  # Toggle if the effect of power pellets should be ignored.
        lockDeltaTime=True,  # When enabled, the game will run at the highest possible speed.
        logging=False,  # Toggle the logging of game-related information to the console while the agent is playing.
        disableVisuals=True  # Toggle the visuals of the game.
    )
