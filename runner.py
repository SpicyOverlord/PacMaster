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
        gameCount=500,
        gameSpeed=1,
        startLevel=0,
        startLives=3,
        ghostsEnabled=True,
        freightEnabled=True,
        lockDeltaTime=False,
        logging=True
    )