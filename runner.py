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

    # agentClass = FirstRealAgent
    agentClass = FinalAgent

    stats = calculatePerformanceOverXGames(
        agentClass=agentClass,
        weightContainer=agentClass.getDefaultWeightContainer(),
        # weightContainer=WeightContainer(
        #     {'fleeThreshold': 0.093, 'pelletLevelDistance': 31.92, 'wayTooCloseThreshold': 54.865,
        #      'tooCloseThreshold': 0.006, 'tooFarAwayThreshold': 14.209, 'wayTooCloseValue': 9474.625,
        #      'tooCloseValue': 46296.786, 'dangerZoneMultiplier': 0.021, 'dangerZoneMiddleMapNodeMultiplier': 0.0,
        #      'ghostInDangerZoneMultiplier': 18.06, 'closestGhostMultiplier': 0.032, 'ghostIsCloserMultiplier': 0.124,
        #      'edgeMultiplier': 2.307}),
        gameCount=50,
        gameSpeed=1,
        startLevel=0,
        startLives=3,
        ghostsEnabled=True,
        freightEnabled=True,
        lockDeltaTime=False,
        logging=True
    )
