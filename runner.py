from PacmanAgentBuilder.Agents.MyFirstAgent import MyFirstAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.runnerFunctions import *

if __name__ == "__main__":
    DebugHelper.disable()
    stats = calculatePerformanceOverXGames(
        agentClass=MyFirstAgent,
        weightContainer=WeightContainer({'fleeThreshold': 0.142, 'pelletLevelDistance': 2.699, 'wayTooCloseThreshold': 60.868, 'tooCloseThreshold': 0.263, 'tooFarAwayThreshold': 1769.249, 'wayTooCloseValue': 864.227, 'tooCloseValue': 47.85, 'dangerZoneMultiplier': 0.485, 'dangerZoneMiddleMapNodeMultiplier': 0.043, 'ghostInDangerZoneMultiplier': 0.002, 'closestGhostMultiplier': 0.579, 'ghostIsCloserMultiplier': 8.302, 'edgeMultiplier': 2.0}),
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
