from PacMaster.agents.Iagent import IAgent
from Pacman_Complete.run import GameController


class GameStats(object):
    def __init__(self, game: GameController, agent: IAgent):
        self.actionsTaken = agent.actionsTaken
        self.score = game.score
        self.levelsCompleted = game.level
        self.totalPelletsEaten = game.level * 240 + agent.pelletsEatenThisLevel
        self.efficiency = self.totalPelletsEaten * 10 / agent.actionsTaken

    @staticmethod
    def calculateCombinedRating(gameStats: list['GameStats']):
        weights = {'efficiency': 1, 'score': 1, 'pellets': 0.8}

        baseScores = [game.score for game in gameStats]
        efficiency = [game.efficiency for game in gameStats]
        totalPelletsEaten = [game.totalPelletsEaten for game in gameStats]

        # Calculate efficiency
        weightedEfficiency = sum(efficiency) / len(efficiency) * weights['efficiency']

        # Calculate total pellets eaten
        normalizedPelletScores = [pelletsEaten / 240 for pelletsEaten in
                                  totalPelletsEaten]  # 240 is the max pellets per level
        weightedPelletScore = sum(normalizedPelletScores) / len(normalizedPelletScores) * weights['pellets']

        # Calculate weighted average score
        normalizedScores = [score / 2600 for score in baseScores]  # 2600 is the max score for a single level
        weightedScore = sum(normalizedScores) / len(normalizedScores) * weights['score']

        print("weighted Efficiency:", weightedEfficiency)
        print("weighted Score:", weightedScore)
        print("weighted Pellet Score:", weightedPelletScore)

        # Combined Score Calculation
        combinedScore = (weightedScore + weightedPelletScore) * weightedEfficiency

        # Statistical Analysis
        median_score = sorted(baseScores)[len(baseScores) // 2]
        mean_score = sum(normalizedScores) / len(normalizedScores)
        variance = sum((s - mean_score) ** 2 for s in normalizedScores) / len(normalizedScores)
        std_deviation = variance ** 0.5

        return {"combinedScore": combinedScore, "medianScore": median_score, "stdDeviation": std_deviation}
