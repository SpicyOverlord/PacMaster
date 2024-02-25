from PacMaster.agents.ScaredAgent import ScaredAgent
from PacMaster.agents.UntrappableAgent import UntrappableAgent
from PacMaster.utils.runnerFunctions import *

# runGameWithHuman()
print(calculatePerformanceOverXGames(UntrappableAgent, gameCount=10, gameSpeed=10, startLevel=0,
                                     ghostsEnabled=True, freightEnabled=True, logging=True))



