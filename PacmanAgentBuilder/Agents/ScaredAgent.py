import pygame

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Iagent import IAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.Map import MapNode
from PacmanAgentBuilder.Utils.observation import Observation
from Pacman_Complete.constants import *
from Pacman_Complete.ghosts import Ghost


class ScaredAgent(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

    def calculateNextMove(self, obs: Observation):
        pacmanPosition = obs.getPacmanPosition()
        mapPos = obs.map.createMapPosition(pacmanPosition)

        # if we are on a node, we can calculate the best direction to go
        if not mapPos.isBetweenMapNodes:
            return self.__getLeastDangerousDirectionFromNode__(obs, obs.map.getNearestMapNode(pacmanPosition))

        # else calculate which of the two directions is the least dangerous
        ghostBetweenMapNodes = obs.getGhostBetweenMapNodes(mapPos.mapNode1, mapPos.mapNode2)
        if ghostBetweenMapNodes is not None:
            return self.__fleeFromGhost__(obs, ghostBetweenMapNodes, mapPos.isXAxis)
        else:
            return self.__getLeastDangerousDirection__(obs, mapPos.mapNode1, mapPos.mapNode2, mapPos.isXAxis)

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
        elif mapNode1DangerLevel == mapNode2DangerLevel:
            return STOP
        else:
            return self.__getDirection__(obs, mapNode2, isXAxis)

    def __getLeastDangerousDirectionFromNode__(self, obs: Observation, onMapNode: MapNode) -> int:
        minNeighbor = None
        minDangerLevel = 99999
        for neighbor in onMapNode.neighborContainers:
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
