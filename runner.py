import os

from PacmanAgentBuilder.Agents.FinalAgent import FinalAgent
from PacmanAgentBuilder.Utils.runnerFunctions import *

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

if __name__ == "__main__":
    agentClass = FinalAgent

    # this will run the agent in 50 games and print the average performance over the 50 games
    stats = calculatePerformanceOverXGames(
        agentClass=agentClass,  # Specify the agent to be evaluated.

        weightContainer=WeightContainer(
            {'fleeThreshold': 7.56977, 'pelletLevelDistance': 0.07855, 'tooCloseThreshold': 223.7031,
             'tooCloseValue': 360948.88277, 'tooFarAwayThreshold': 0.00077, 'dangerZoneMultiplier': 0.0001,
             'dangerZoneMiddleMapNodeMultiplier': 1.11383, 'ghostIsCloserMultiplier': 0.04785,
             'edgeMultiplier': 0.21505, 'pelletLevelDistanceInDangerLevel': 178.28374,
             'pelletsInDangerLevelMultiplier': 0.11514, 'distanceToPacManMultiplier': 0.01946,
             'PelletIslandDistance': 0.13236, 'IslandSizeMultiplier': 0.00995, 'IslandDistanceMultiplier': 46.83615,
             'ghostMultiplier': 0.20619, 'blinky': 0.14664, 'pinky': 1590.88478, 'inky': 0.01836, 'clyde': 0.26981}
        ),

        gameCount=200,  # Number of games the agent will play.
        gameSpeed=1,  # Sets the speed of the game from 0.1 (slow) to 15 (fast).
        startLevel=0,  # Choose the starting level for the agent (0 for level one, 1 for level two, and so on).
        startLives=3,  # Choose the number of lives the agent will start with.
        ghostsEnabled=True,  # Toggle ghosts on or off.
        freightEnabled=True,  # Toggle if the effect of power pellets should be ignored.
        lockDeltaTime=True,  # When enabled, the game will run at the highest possible speed.
        logging=True  # Toggle the logging of game-related information to the console while the agent is playing.
    )
