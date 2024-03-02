from PacMaster.agents.Iagent import IAgent
from Pacman_Complete.run import GameController


class GameStats(object):
    def __init__(self, game: GameController, agent: IAgent):
        self.actionsTaken = agent.actionsTaken
        self.score = game.score
        self.levelsCompleted = game.level
        self.totalPelletsEaten = game.level * 240 + agent.pelletsEatenThisLevel
        self.efficiency = self.totalPelletsEaten * 10 / agent.actionsTaken / 2

    def __str__(self):
        return f"GameStats(score={self.score}, efficiency={round(self.efficiency, 3)}, totalPelletsEaten={self.totalPelletsEaten}, actionsTaken={self.actionsTaken}, levelsCompleted={self.levelsCompleted})"

    @staticmethod
    def calculateCombinedRating(gameStats: list['GameStats']):
        weights = {'score': 0.5, 'pellets': 1.2, 'efficiency': 0.3}

        baseScores = [game.score for game in gameStats]
        efficiency = [game.efficiency for game in gameStats]
        totalPelletsEaten = [game.totalPelletsEaten for game in gameStats]

        # Calculate average efficiency
        averageEfficiency = sum(efficiency) / len(efficiency)

        # calculate average and max level reached
        averageLevelsCompleted = sum([game.levelsCompleted for game in gameStats]) / len(gameStats)
        weighedAverageLevel = (averageLevelsCompleted * 0.5) + 1
        maxLevelCompleted = max([game.levelsCompleted for game in gameStats])

        # Calculate total pellets eaten
        maxPelletsPerLevel = 240
        normalizedPelletScores = [pelletsEaten / maxPelletsPerLevel for pelletsEaten in totalPelletsEaten]
        weightedAveragePelletScore = sum(normalizedPelletScores) / len(normalizedPelletScores) * weights['pellets']

        # Calculate weighted average score
        maxBaseScorePerLevel = 2600
        normalizedBaseScores = [score / maxBaseScorePerLevel for score in baseScores]
        weightedAverageBaseScore = sum(normalizedBaseScores) / len(normalizedBaseScores) * weights['score']

        # Combined Score Calculation
        # basically makes averageEfficiency only change 30% of the combined score
        combinedScore = weights['efficiency'] * (averageEfficiency + 1) * (weightedAverageBaseScore + weightedAveragePelletScore)
        # # multiply to make the score higher if the agent reaches higher levels
        combinedScore *= weighedAverageLevel

        # Statistical Analysis
        medianScore = sorted(baseScores)[len(baseScores) // 2]
        averageNormalizedScore = sum(normalizedBaseScores) / len(normalizedBaseScores)
        variance = sum((s - averageNormalizedScore) ** 2 for s in normalizedBaseScores) / len(normalizedBaseScores)
        stdDeviation = variance ** 0.5
        averageScore = sum(baseScores) / len(baseScores)

        return {"combinedScore": round(combinedScore, 3),
                "averageEfficiency": round(averageEfficiency, 3),
                "weightedAverageBaseScore": round(weightedAverageBaseScore, 3),
                "weightedAveragePelletScore": round(weightedAveragePelletScore, 3),
                "averageLevelsCompleted": round(averageLevelsCompleted, 3),
                "maxLevelCompleted": maxLevelCompleted,

                "medianScore": medianScore,
                "averageScore": round(averageScore, 3),
                "maxScore": max(baseScores),
                "minScore": min(baseScores),
                "stdDeviation": round(stdDeviation, 3)}
