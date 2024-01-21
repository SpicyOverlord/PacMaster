from PacMaster.agents.Iagent import IAgent
from Pacman_Complete.run import GameController


def runGameWithHuman() -> int:
    game = GameController(gameSpeed=1, startLives=3, isHumanPlayer=True)
    game.startGame()
    while True:
        game.update()
        if game.gameOver:
            return game.score


def runGameWithAgent(agentClass: type[IAgent], gameSpeed=1, startLives=3) -> int:
    game = GameController(gameSpeed=gameSpeed, startLives=startLives, isHumanPlayer=False)
    agent = agentClass(gameController=game)
    game.startGame(agent=agent)
    while True:
        game.update()
        if game.gameOver:
            return game.score


def avgOfX(agentClass: type[IAgent], gameCount: int) -> float:
    scores = []
    for i in range(gameCount):
        scores.append(runGameWithAgent(agentClass, gameSpeed=10, startLives=1))
    return sum(scores) / len(scores)
