from PacMaster.agents.ScaredAgent import ScaredAgent
from PacMaster.utils.runnerFunctions import *

# runGameWithHuman()
print(calculatePerformanceOverXGames(ScaredAgent, gameCount=50, gameSpeed=1, startLevel=4, ghostsEnabled=False))



