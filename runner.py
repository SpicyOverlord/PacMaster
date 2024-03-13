import os

import numpy as np

from PacmanAgentBuilder.Agents.CollectorAgent import CollectorAgent
from PacmanAgentBuilder.Agents.FinalAgent import FinalAgent

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from PacmanAgentBuilder.Agents.FirstRealAgent import FirstRealAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.runnerFunctions import *

if __name__ == "__main__":
    # DebugHelper.disable()

    agentClass = FirstRealAgent
    # agentClass = FinalAgent

    stats = calculatePerformanceOverXGames(
        agentClass=agentClass,
        weightContainer=agentClass.getBestWeightContainer(),
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

    # weightList = [
    #     WeightContainer({'fleeThreshold': 0.05, 'pelletLevelDistance': 15.939, 'wayTooCloseThreshold': 16.024,
    #                      'tooCloseThreshold': 71.731, 'tooFarAwayThreshold': 2069.434, 'wayTooCloseValue': 3089.918,
    #                      'tooCloseValue': 1456.791, 'dangerZoneMultiplier': 0.005,
    #                      'dangerZoneMiddleMapNodeMultiplier': 0.001, 'ghostInDangerZoneMultiplier': 5.431,
    #                      'closestGhostMultiplier': 0.144, 'ghostIsCloserMultiplier': 2.208,
    #                      'edgeMultiplier': 3.232}),
    #     WeightContainer({'fleeThreshold': 0.168, 'pelletLevelDistance': 3.438, 'wayTooCloseThreshold': 70.268,
    #                      'tooCloseThreshold': 0.008, 'tooFarAwayThreshold': 2039.184, 'wayTooCloseValue': 394.23,
    #                      'tooCloseValue': 195.778, 'dangerZoneMultiplier': 1.123,
    #                      'dangerZoneMiddleMapNodeMultiplier': 0.757, 'ghostInDangerZoneMultiplier': 0.0,
    #                      'closestGhostMultiplier': 0.0, 'ghostIsCloserMultiplier': 5.169, 'edgeMultiplier': 4.045}),
    #     WeightContainer({'fleeThreshold': 5.659, 'pelletLevelDistance': 12.484, 'wayTooCloseThreshold': 78.651,
    #                      'tooCloseThreshold': 1751.564, 'tooFarAwayThreshold': 1631.598,
    #                      'wayTooCloseValue': 48344.922,
    #                      'tooCloseValue': 22.455, 'dangerZoneMultiplier': 2.52,
    #                      'dangerZoneMiddleMapNodeMultiplier': 4.753, 'ghostInDangerZoneMultiplier': 4.174,
    #                      'closestGhostMultiplier': 2.408, 'ghostIsCloserMultiplier': 348.426,
    #                      'edgeMultiplier': 0.032}),
    #     WeightContainer({'fleeThreshold': 0.142, 'pelletLevelDistance': 2.699, 'wayTooCloseThreshold': 60.868,
    #                      'tooCloseThreshold': 0.263, 'tooFarAwayThreshold': 1769.249, 'wayTooCloseValue': 864.227,
    #                      'tooCloseValue': 47.85, 'dangerZoneMultiplier': 0.485,
    #                      'dangerZoneMiddleMapNodeMultiplier': 0.043, 'ghostInDangerZoneMultiplier': 0.002,
    #                      'closestGhostMultiplier': 0.579, 'ghostIsCloserMultiplier': 8.302, 'edgeMultiplier': 2.0}),
    #     WeightContainer({'fleeThreshold': 0.153, 'pelletLevelDistance': 2.144, 'wayTooCloseThreshold': 64.359,
    #                      'tooCloseThreshold': 0.34, 'tooFarAwayThreshold': 1195.206, 'wayTooCloseValue': 2600.674,
    #                      'tooCloseValue': 123.482, 'dangerZoneMultiplier': 0.407,
    #                      'dangerZoneMiddleMapNodeMultiplier': 0.873, 'ghostInDangerZoneMultiplier': 0.0,
    #                      'closestGhostMultiplier': 0.275, 'ghostIsCloserMultiplier': 8.302,
    #                      'edgeMultiplier': 3.175}),
    #     WeightContainer({'fleeThreshold': 0.05, 'pelletLevelDistance': 15.939, 'wayTooCloseThreshold': 20.577,
    #                      'tooCloseThreshold': 71.731, 'tooFarAwayThreshold': 1979.009, 'wayTooCloseValue': 3423.479,
    #                      'tooCloseValue': 1355.534, 'dangerZoneMultiplier': 0.005,
    #                      'dangerZoneMiddleMapNodeMultiplier': 0.001, 'ghostInDangerZoneMultiplier': 5.99,
    #                      'closestGhostMultiplier': 0.144, 'ghostIsCloserMultiplier': 2.612,
    #                      'edgeMultiplier': 2.109}),
    #     WeightContainer({'fleeThreshold': 0.035, 'pelletLevelDistance': 15.939, 'wayTooCloseThreshold': 20.949,
    #                      'tooCloseThreshold': 71.731, 'tooFarAwayThreshold': 1979.009, 'wayTooCloseValue': 4372.183,
    #                      'tooCloseValue': 1363.13, 'dangerZoneMultiplier': 0.005,
    #                      'dangerZoneMiddleMapNodeMultiplier': 0.001, 'ghostInDangerZoneMultiplier': 5.431,
    #                      'closestGhostMultiplier': 0.144, 'ghostIsCloserMultiplier': 2.612,
    #                      'edgeMultiplier': 1.237})
    # ]
