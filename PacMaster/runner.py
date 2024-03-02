from PacMaster.agents.CollectorAgent import CollectorAgent
from PacMaster.agents.FirstRealAgent import FirstRealAgent
from PacMaster.agents.ScaredAgent import ScaredAgent
from PacMaster.agents.UntrappableAgent import UntrappableAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.runnerFunctions import *

# runGameWithHuman()
DebugHelper.disable()
for i in range(1000):
    stats = calculatePerformanceOverXGames(FirstRealAgent, gameCount=50, gameSpeed=15, startLevel=0, startLives=1,
                                           ghostsEnabled=True, freightEnabled=True, logging=False)
    print(stats)
