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
        decayRate=0.99,  # The rate at which the alpha and rho values will decay.
        decayInterval=10,  # The interval at which the alpha and rho values will decay.
        saveInterval=200,  # The interval at which the Q-values will be saved to a file.
        gameCount=500,  # Number of games the agent will play.
        gameSpeed=1,  # Sets the speed of the game from 0.1 (slow) to 15 (fast).
        startLevel=0,  # Choose the starting level for the agent (0 for level one, 1 for level two, and so on).
        startLives=5,  # Choose the number of lives the agent will start with.
        ghostsEnabled=True,  # Toggle ghosts on or off.
        freightEnabled=True,  # Toggle if the effect of power pellets should be ignored.
        lockDeltaTime=True,  # When enabled, the game will run at the highest possible speed.
        logging=True,  # Toggle the logging of game-related information to the console while the agent is playing.
        disableVisuals=True  # Toggle the visuals of the game.
    )
