from PacmanAgentBuilder.Agents.MyFirstAgent import MyFirstAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.runnerFunctions import *

if __name__ == "__main__":
    DebugHelper.disable()
    stats = calculatePerformanceOverXGames(
        agentClass=MyFirstAgent,
        weightContainer=WeightContainer({'fleeThreshold': 0.169, 'pelletLevelDistance': 3.336, 'wayTooCloseThreshold': 93.95, 'tooCloseThreshold': 4.068, 'tooFarAwayThreshold': 4896.327, 'wayTooCloseValue': 1954.034, 'tooCloseValue': 229.013, 'dangerZoneMultiplier': 0.765, 'dangerZoneMiddleMapNodeMultiplier': 0.313, 'ghostInDangerZoneMultiplier': 0.142, 'closestGhostMultiplier': 0.003, 'ghostIsCloserMultiplier': 6.329, 'edgeMultiplier': 2.466}),
        # weightContainer=None,
        gameCount=10,
        gameSpeed=1,
        startLevel=0,
        startLives=1,
        ghostsEnabled=True,
        freightEnabled=True,
        lockDeltaTime=False,
        logging=True
    )
