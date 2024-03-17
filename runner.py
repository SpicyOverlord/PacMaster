import os

import numpy as np

from PacmanAgentBuilder.Agents.CollectorAgent import CollectorAgent
from PacmanAgentBuilder.Agents.CollectorAgent2 import CollectorAgent2
from PacmanAgentBuilder.Agents.FinalAgent import FinalAgent

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

from PacmanAgentBuilder.Agents.FirstRealAgent import FirstRealAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.runnerFunctions import *

if __name__ == "__main__":
    # DebugHelper.disable()

    agentClass = FirstRealAgent
    # agentClass = FinalAgent
    # agentClass = CollectorAgent2

    stats = calculatePerformanceOverXGames(
        agentClass=agentClass,
        # weightContainer=agentClass.getDefaultWeightContainer(),
        weightContainer=WeightContainer(
            {'fleeThreshold': 0.01119, 'pelletLevelDistance': 2.83253, 'wayTooCloseThreshold': 32.68235,
             'tooCloseThreshold': 8e-05, 'tooFarAwayThreshold': 1219.81699, 'wayTooCloseValue': 352.64291,
             'tooCloseValue': 87.99661, 'dangerZoneMultiplier': 8.68754, 'dangerZoneMiddleMapNodeMultiplier': 0.00206,
             'ghostInDangerZoneMultiplier': 0.0, 'closestGhostMultiplier': 0.0, 'ghostIsCloserMultiplier': 3.11343,
             'edgeMultiplier': 1.75577}
        ),
        gameCount=100,
        gameSpeed=1,
        startLevel=0,
        startLives=3,
        ghostsEnabled=True,
        freightEnabled=True,
        lockDeltaTime=True,
        logging=True
    )
