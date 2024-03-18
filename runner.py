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

    # agentClass = FirstRealAgent
    agentClass = FinalAgent
    # agentClass = CollectorAgent2

    stats = calculatePerformanceOverXGames(
        agentClass=agentClass,
        weightContainer=agentClass.getDefaultWeightContainer(),
        # weightContainer=WeightContainer(
        #     {'fleeThreshold': 0.01012, 'pelletLevelDistance': 3.63027, 'wayTooCloseThreshold': 35.26691,
        #      'tooCloseThreshold': 0.003, 'tooFarAwayThreshold': 2496.83669, 'wayTooCloseValue': 597.86046,
        #      'tooCloseValue': 591.83419, 'dangerZoneMultiplier': 10.02436, 'dangerZoneMiddleMapNodeMultiplier': 0.00206,
        #      'ghostInDangerZoneMultiplier': 37.7879, 'closestGhostMultiplier': 0.0, 'ghostIsCloserMultiplier': 15.93602,
        #      'edgeMultiplier': 2.25542}
        # ),
        gameCount=50,
        gameSpeed=1,
        startLevel=0,
        startLives=1,
        ghostsEnabled=True,
        freightEnabled=True,
        lockDeltaTime=False,
        logging=True
    )
