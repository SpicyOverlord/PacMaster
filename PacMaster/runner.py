from PacMaster.agents.Iagent import IAgent
from PacMaster.agents.FirstAgent import FirstAgent
from Pacman_Complete.run import GameController


def runGameWithAgent(agentClass: type[IAgent]) -> int:
    game = GameController(gameSpeed=3, startLives=3, isHumanPlayer=False)
    agent = agentClass(gameController=game)
    game.startGame(agent=agent)
    while True:
        game.update()
        if game.gameOver:
            return game.score


for i in range(2):
    print("score:", runGameWithAgent(FirstAgent))
