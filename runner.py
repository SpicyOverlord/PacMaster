import os

from PacmanAgentBuilder.Agents.QLearningAgent import QLearningAgent
from PacmanAgentBuilder.Utils.runnerFunctions import *

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

if __name__ == "__main__":
    # agentClass = FinalAgent
    agentClass = QLearningAgent

    # this will run the agent in 50 games and print the average performance over the 50 games
    stats = calculatePerformanceOverXGames(
        agentClass=agentClass,  # Specify the agent to be evaluated.
        saveInterval=10000,  # The interval at which the Q-values will be saved to a file.
        gameCount=5,  # Number of games the agent will play.
        gameSpeed=2,  # Sets the speed of the game from 0.1 (slow) to 15 (fast).
        startLevel=0,  # Choose the starting level for the agent (0 for level one, 1 for level two, and so on).
        startLives=5,  # Choose the number of lives the agent will start with.
        ghostsEnabled=True,  # Toggle ghosts on or off.
        freightEnabled=True,  # Toggle if the effect of power pellets should be ignored.
        logging=True,  # Toggle the logging of game-related information to the console while the agent is playing.
        disableVisuals=False  # Toggle the visuals of the game.
    )
