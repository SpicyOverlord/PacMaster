from PacMaster.agents.CollectorAgent import CollectorAgent
from PacMaster.agents.FirstRealAgent import FirstRealAgent
from PacMaster.agents.ScaredAgent import ScaredAgent
from PacMaster.agents.UntrappableAgent import UntrappableAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.runnerFunctions import *
import time

from PacMaster.utils.utils import secondsToTime

DebugHelper.disable()
scores = []
times = []
for i in range(1000):
    start_time = time.time()
    stats = calculatePerformanceOverXGames(FirstRealAgent, gameCount=10, gameSpeed=1, startLevel=0, startLives=1,
                                           ghostsEnabled=True, freightEnabled=True, logging=False, lockDeltaTime=True)
    end_time = time.time()
    elapsed_time = end_time - start_time
    times.append(elapsed_time)
    scores.append(stats['combinedScore'])
    # print(stats)
    estimatedSecondsLeft = sum(times) / len(times)
    print(f"{i} score: {round(stats['combinedScore'],2)}  -  "
          f"Average: {round(sum(scores) / len(scores),2)}  -  "
          f"Time: {secondsToTime(estimatedSecondsLeft)}  -  "
          f"Estimated: {secondsToTime(estimatedSecondsLeft * (1000 - i))}")
