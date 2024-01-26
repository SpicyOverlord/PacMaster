import pygame

from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.map import MapNode
from PacMaster.utils.observation import Observation
from Pacman_Complete.constants import *
from Pacman_Complete.ghosts import Ghost
from Pacman_Complete.vector import Vector2


class UntrappableAgent(IAgent):
    def __init__(self, gameController):
        super().__init__(gameController)
        self.last = []

    def calculateNextMove(self):
        obs = Observation(self.gameController)
        self.takeStats(obs)

        DebugHelper.drawMap(obs)
        DebugHelper.drawDangerLevels(obs)

        # DebugHelper.drawGhostPaths(obs)
        # DebugHelper.pauseGame()

        pacmanPosition = obs.getPacmanPosition()
        mapPos = obs.map.createMapPosition(pacmanPosition)

        if len(self.last) > 0:
            DebugHelper.drawDashedPath(self.last, DebugHelper.GREEN)
        if mapPos.isInDangerZone:
            DebugHelper.drawDangerZone(mapPos.dangerZone)

        if mapPos.isInDangerZone and mapPos.dangerZone.isDangerous:
            escapeTarget = mapPos.dangerZone.escapeEdgeMapNode.position
            DebugHelper.drawDot(escapeTarget, DebugHelper.PURPLE, 10)

            escapePath, pacdist = obs.map.calculateShortestPath(pacmanPosition, escapeTarget)

            closestGhost = obs.getClosestGhost()
            ghostPath, ghostdist = obs.map.calculateShortestPath(closestGhost.position, escapeTarget,
                                                                 True, closestGhost.direction)

            self.last = ghostPath
            # DebugHelper.pauseGame()
            # print(mapPos.dangerZone)
            # print()
            return self.__getDirection__(obs, escapePath[1])

        # if we are on a node, we can calculate the best direction to go
        if not mapPos.isBetweenMapNodes:
            return self.__getLeastDangerousDirectionFromNode__(obs, obs.map.getClosestMapNode(pacmanPosition))

        # else calculate which of the two directions is the least dangerous
        ghostBetweenMapNodes = obs.getGhostBetweenMapNodes(mapPos.mapNode1, mapPos.mapNode2)
        if ghostBetweenMapNodes is not None:
            return self.__fleeFromGhost__(obs, ghostBetweenMapNodes, mapPos.isXAxis)
        else:
            return self.__getLeastDangerousDirection__(obs, mapPos.mapNode1, mapPos.mapNode2, mapPos.isXAxis)

    def __getDirection__(self, obs: Observation, target: Vector2) -> int:
        pacmanPosition = obs.getPacmanPosition()
        if pacmanPosition.y == target.y:
            if pacmanPosition.x < target.x:
                return RIGHT
            else:
                return LEFT
        else:
            if pacmanPosition.y < target.y:
                return DOWN
            else:
                return UP

    def __getLeastDangerousDirection__(self, obs: Observation, mapNode1: MapNode, mapNode2: MapNode,
                                       isXAxis: bool) -> int:
        mapNode1DangerLevel = obs.calculateDangerLevel(mapNode1.position)
        mapNode2DangerLevel = obs.calculateDangerLevel(mapNode2.position)
        if mapNode1DangerLevel < mapNode2DangerLevel:
            return self.__getDirection__(obs, mapNode1.position)
        elif mapNode1DangerLevel == mapNode2DangerLevel:
            return STOP
        else:
            return self.__getDirection__(obs, mapNode2.position)

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
