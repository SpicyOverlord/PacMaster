from PacMaster.agents.CollectorAgent import CollectorAgent
from PacMaster.agents.FirstRealAgent import FirstRealAgent
from PacMaster.agents.ScaredAgent import ScaredAgent
from PacMaster.agents.UntrappableAgent import UntrappableAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.runnerFunctions import *

DebugHelper.disable()
calculatePerformanceOverXGames(HumanAgent, gameCount=50, gameSpeed=1, startLevel=0, startLives=1,
                               ghostsEnabled=True, freightEnabled=True, logging=True, lockFrameRate=True)
