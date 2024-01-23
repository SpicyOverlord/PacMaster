from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.map import MapNode
from PacMaster.utils.observation import Observation
from PacMaster.utils.utils import manhattenDistance
from Pacman_Complete.constants import *
from Pacman_Complete.ghosts import Ghost


class FirstAgent(IAgent):
    def __init__(self, gameController):
        super().__init__(gameController)

    def calculateNextMove(self):
        obs = Observation(self.gameController)
        self.takeStats(obs)

        # if we are on a node, we can calculate the best direction to go
        onMapNode = obs.getOnNode()
        if onMapNode is not None:
            return self.__getLeastDangerousDirectionFromNode__(obs, obs.getClosestMapNode())

        # else calculate which of the two directions is the least dangerous
        mapNode1, mapNode2, isXAxis = obs.getBetweenMapNodes()
        if mapNode1 is None:
            raise Exception("No map node pair found around pacman")

        ghostBetweenMapNodes = obs.getGhostBetweenMapNodes(mapNode1, mapNode2)
        if ghostBetweenMapNodes is not None:
            return self.__fleeFromGhost__(obs, ghostBetweenMapNodes, isXAxis)
        else:
            return self.__getLeastDangerousDirection__(obs, mapNode1, mapNode2, isXAxis)

    def __getDirection__(self, obs: Observation, mapNode: MapNode, isXAxis: bool) -> int:
        if isXAxis:
            if obs.getPacmanPosition().x < mapNode.position.x:
                return RIGHT
            else:
                return LEFT
        else:
            if obs.getPacmanPosition().y < mapNode.position.y:
                return DOWN
            else:
                return UP

    def __getLeastDangerousDirection__(self, obs: Observation, mapNode1: MapNode, mapNode2: MapNode,
                                       isXAxis: bool) -> int:
        mapNode1DangerLevel = obs.calculateDangerLevel(mapNode1.position)
        mapNode2DangerLevel = obs.calculateDangerLevel(mapNode2.position)
        if mapNode1DangerLevel < mapNode2DangerLevel:
            return self.__getDirection__(obs, mapNode1, isXAxis)
        else:
            return self.__getDirection__(obs, mapNode2, isXAxis)

    def __getLeastDangerousDirectionFromNode__(self, obs: Observation, onMapNode: MapNode) -> int:
        minNeighbor = None
        minDangerLevel = 99999
        for neighbor in onMapNode.neighbors:
            ghostBetween = obs.getGhostBetweenMapNodes(onMapNode, neighbor.mapNode)
            if ghostBetween is not None:
                continue

            dangerLevel = obs.calculateDangerLevel(neighbor.mapNode.position)
            if dangerLevel < minDangerLevel:
                minNeighbor = neighbor
                minDangerLevel = dangerLevel

        if minNeighbor is None:
            return STOP
        return minNeighbor.direction

    def __fleeFromGhost__(self, obs: Observation, ghost: Ghost, isXAxis: bool) -> int:
        if isXAxis:
            if obs.getPacmanPosition().x < ghost.position.x:
                return LEFT
            else:
                return RIGHT
        else:
            if obs.getPacmanPosition().y < ghost.position.y:
                return UP
            else:
                return DOWN
