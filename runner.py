import numpy as np

from PacmanAgentBuilder.Agents.MyFirstAgent import MyFirstAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.runnerFunctions import *


def bootstrap_confidence_interval(agent, stats: list[GameStats], confidence_level=0.95):
    scores = [stat.getScore() for stat in stats]
    bootstrapped_means = []

    # We create bootstrap samples and calculate the means
    for _ in range(len(stats)):
        sample = np.random.choice(scores, size=len(scores), replace=True)
        bootstrapped_means.append(np.mean(sample))

    # Now we calculate the confidence interval
    lower_percentile = ((1.0 - confidence_level) / 2.0) * 100
    upper_percentile = (1.0 - ((1.0 - confidence_level) / 2.0)) * 100
    lower_confidence = np.percentile(bootstrapped_means, lower_percentile)
    upper_confidence = np.percentile(bootstrapped_means, upper_percentile)

    return np.mean(scores), lower_confidence, upper_confidence


if __name__ == "__main__":
    DebugHelper.disable()

    allStats = []
    for j in range(100):

        statList = []
        for i in range(100):
            if (i + 1) % 10 == 0:
                print(f"{i + 1} ", end=" ")

            stats = runGameWithAgent(
                agentClass=MyFirstAgent,
                weightContainer=MyFirstAgent.getBestWeightContainer(),
                # weightContainer=None,
                gameSpeed=1,
                startLevel=0,
                startLives=1,
                ghostsEnabled=True,
                freightEnabled=True,
                lockDeltaTime=True
            )
            statList.append(stats)
            allStats.append(stats)

        print(f"CombinedScore: {GameStats.calculatePerformance(statList)['combinedScore']}")
        mean, lower, upper = bootstrap_confidence_interval(MyFirstAgent, statList)
        print(f"Mean: {mean}, Lower: {lower}, Upper: {upper}")
        print(f"------------------- {len(allStats)} --------------------------")
        print(f"CombinedScore: {GameStats.calculatePerformance(allStats)['combinedScore']}")
        mean, lower, upper = bootstrap_confidence_interval(MyFirstAgent, allStats)
        print(f"Mean: {mean}, Lower: {lower}, Upper: {upper}")
        print()
        print()
