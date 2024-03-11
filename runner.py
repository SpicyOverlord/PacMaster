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
    stats = calculatePerformanceOverXGames(
        agentClass=MyFirstAgent,
        weightContainer=WeightContainer({'fleeThreshold': 0.142, 'pelletLevelDistance': 2.699, 'wayTooCloseThreshold': 60.868, 'tooCloseThreshold': 0.263, 'tooFarAwayThreshold': 1769.249, 'wayTooCloseValue': 864.227, 'tooCloseValue': 47.85, 'dangerZoneMultiplier': 0.485, 'dangerZoneMiddleMapNodeMultiplier': 0.043, 'ghostInDangerZoneMultiplier': 0.002, 'closestGhostMultiplier': 0.579, 'ghostIsCloserMultiplier': 8.302, 'edgeMultiplier': 2.0}),
        # weightContainer=None,
        gameCount=100,
        gameSpeed=1,
        startLevel=0,
        startLives=1,
        ghostsEnabled=True,
        freightEnabled=True,
        lockDeltaTime=False,
        logging=True
    )

    exit()

    for j in range(100):
        statList = []
        for i in range(50):
            print(f"{i+1} ", end=" ")

            stats = runGameWithAgent(
                agentClass=MyFirstAgent,
                weightContainer=WeightContainer(
                    {'fleeThreshold': 0.05, 'pelletLevelDistance': 15.939, 'wayTooCloseThreshold': 16.024,
                     'tooCloseThreshold': 71.731, 'tooFarAwayThreshold': 2069.434, 'wayTooCloseValue': 3089.918,
                     'tooCloseValue': 1456.791, 'dangerZoneMultiplier': 0.005, 'dangerZoneMiddleMapNodeMultiplier': 0.001,
                     'ghostInDangerZoneMultiplier': 5.431, 'closestGhostMultiplier': 0.144,
                     'ghostIsCloserMultiplier': 2.208, 'edgeMultiplier': 3.232}),
                # weightContainer=None,
                gameSpeed=1,
                startLevel=0,
                startLives=1,
                ghostsEnabled=True,
                freightEnabled=True,
                lockDeltaTime=True
            )
            statList.append(stats)

        print()
        print(GameStats.calculatePerformance(statList))
        mean, lower, upper = bootstrap_confidence_interval(MyFirstAgent, statList)
        print(f"Mean: {mean}, Lower: {lower}, Upper: {upper}")
        print()

