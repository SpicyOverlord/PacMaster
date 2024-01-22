from PacMaster.agents.Iagent import IAgent
from Pacman_Complete.run import GameController


class GameStats(object):
    def __init__(self, game: GameController, agent: IAgent):
        self.actionsTaken = agent.actionsTaken
        self.score = game.score
        self.levelsCompleted = game.level
        self.efficiency = game.score / agent.actionsTaken
        self.riskManagement = agent.dangerLevelSum / agent.actionsTaken
