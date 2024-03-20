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
    DebugHelper.disable()

    # agentClass = FirstRealAgent
    agentClass = FinalAgent
    # agentClass = CollectorAgent2

    stats = calculatePerformanceOverXGames(
        agentClass=agentClass,
        # weightContainer=agentClass.getDefaultWeightContainer(),
        weightContainer=WeightContainer(
            {'fleeThreshold': 14.0415, 'pelletLevelDistance': 26866.3008, 'tooCloseThreshold': 36.72778,
             'tooCloseValue': 45851.42127, 'tooFarAwayThreshold': 754.99757, 'dangerZoneMultiplier': 9.83667,
             'dangerZoneMiddleMapNodeMultiplier': 2.26291, 'ghostIsCloserMultiplier': 0.26211,
             'edgeMultiplier': 0.07031, 'pelletLevelDistanceInDangerLevel': 31289.31605,
             'pelletsInDangerLevelMultiplier': 33.29812, 'distanceToPacManMultiplier': 42.11629,
             'PelletIslandDistance': 1518.14981, 'IslandSizeMultiplier': 206.53291,
             'IslandDistanceMultiplier': 1086.47174, 'ghostMultiplier': 309.08014, 'blinky': 287.69802,
             'pinky': 16.02381, 'inky': 84.06536, 'clyde': 362.14643}
        ),
        gameCount=5,
        gameSpeed=1,
        startLevel=0,
        startLives=1,
        ghostsEnabled=True,
        freightEnabled=True,
        lockDeltaTime=True,
        logging=True
    )
