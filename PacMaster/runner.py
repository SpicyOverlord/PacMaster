from PacMaster.agents.CollectorAgent import CollectorAgent
from PacMaster.agents.FirstRealAgent import FirstRealAgent
from PacMaster.agents.ScaredAgent import ScaredAgent
from PacMaster.agents.UntrappableAgent import UntrappableAgent
from PacMaster.utils.runnerFunctions import *

# runGameWithHuman()
stats = calculatePerformanceOverXGames(FirstRealAgent, gameCount=20, gameSpeed=10, startLevel=0,
                                       ghostsEnabled=True, freightEnabled=True, logging=True)
