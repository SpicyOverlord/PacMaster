from PacmanAgentBuilder.Agents.MyFirstAgent import MyFirstAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.runnerFunctions import *

if __name__ == "__main__":
    DebugHelper.disable()
    stats = calculatePerformanceOverXGames(
        agentClass=MyFirstAgent,  # Specify the agent to be evaluated.
        weightContainer=None,  # Specify the weights to be used by the agent. If None, the default weights will be used.
        gameCount=50,  # Number of games the agent will play.
        gameSpeed=1,  # Sets the speed of the game from 0.1 (slow) to 5 (fast). For a higher speed, enable lockDeltaTime.
        startLevel=0,  # Choose the starting level for the agent (0 for level one, 1 for level two, and so on).
        ghostsEnabled=True,  # Toggle ghosts on or off.
        freightEnabled=True,  # Toggle if the effect of power pellets should be ignored.
        lockDeltaTime=True,  # When enabled, the game will run at the highest possible speed.
        logging=True  # Toggle the logging of game-related information to the console while the agent is playing.
    )
