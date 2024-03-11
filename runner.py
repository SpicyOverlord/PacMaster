from PacmanAgentBuilder.Agents.MyFirstAgent import MyFirstAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.runnerFunctions import *

if __name__ == "__main__":
    DebugHelper.disable()
    stats = calculatePerformanceOverXGames(
        agentClass=MyFirstAgent,
        weightContainer=WeightContainer({'fleeThreshold': 0.05, 'pelletLevelDistance': 15.939, 'wayTooCloseThreshold': 16.024, 'tooCloseThreshold': 71.731, 'tooFarAwayThreshold': 2069.434, 'wayTooCloseValue': 3089.918, 'tooCloseValue': 1456.791, 'dangerZoneMultiplier': 0.005, 'dangerZoneMiddleMapNodeMultiplier': 0.001, 'ghostInDangerZoneMultiplier': 5.431, 'closestGhostMultiplier': 0.144, 'ghostIsCloserMultiplier': 2.208, 'edgeMultiplier': 3.232}),
        # weightContainer=None,
        gameCount=100,
        gameSpeed=1,
        startLevel=0,
        startLives=1,
        ghostsEnabled=True,
        freightEnabled=True,
        lockDeltaTime=True,
        logging=True
    )
