from PacMaster.agents.ScaredAgent import ScaredAgent
from PacMaster.agents.UntrappableAgent import UntrappableAgent
from PacMaster.utils.runnerFunctions import *

# runGameWithHuman()
print(calculatePerformanceOverXGames(HumanAgent, gameCount=50, gameSpeed=0.2, startLevel=0, ghostsEnabled=True, freightEnabled=False))



