from PacMaster.agents.CollectorAgent import CollectorAgent
from PacMaster.agents.ScaredAgent import ScaredAgent
from PacMaster.agents.UntrappableAgent import UntrappableAgent
from PacMaster.utils.runnerFunctions import *

# runGameWithHuman()
print(calculatePerformanceOverXGames(CollectorAgent, gameCount=20, gameSpeed=3, startLevel=0,
                                     ghostsEnabled=False, freightEnabled=False, logging=True))



