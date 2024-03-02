from PacMaster.agents.CollectorAgent import CollectorAgent
from PacMaster.agents.FirstRealAgent import FirstRealAgent
from PacMaster.agents.ScaredAgent import ScaredAgent
from PacMaster.agents.UntrappableAgent import UntrappableAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.runnerFunctions import *
import time

DebugHelper.disable()
scores = []
times = []
for i in range(1000):
    start_time = time.time()
    stats = calculatePerformanceOverXGames(HumanAgent, gameCount=50, gameSpeed=1, startLevel=0, startLives=1,
                                           ghostsEnabled=True, freightEnabled=True, logging=False, lockDeltaTime=True)
    end_time = time.time()
    elapsed_time = end_time - start_time
    times.append(elapsed_time)
    scores.append(stats['combinedScore'])
    # print(stats)
    estimatedSecondsLeft = sum(times) / len(times)
    print(f"{i} Average score: {sum(scores) / len(scores)}  -  Average time: {int(estimatedSecondsLeft / 3600)}h "
          f"{int(estimatedSecondsLeft / 60 % 60)}m "
          f"{int(estimatedSecondsLeft % 60)}s")
