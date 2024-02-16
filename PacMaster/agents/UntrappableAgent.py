import pygame

from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.map import MapNode
from PacMaster.utils.observation import Observation
from PacMaster.utils.utils import manhattanDistance
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

        # DebugHelper.drawMap(obs)
        # DebugHelper.drawDangerLevels(obs)

        # DebugHelper.drawGhostPaths(obs)

        pacmanPosition = obs.getPacmanPosition()
        mapPos = obs.map.createMapPosition(pacmanPosition)

        # if pacmanPosition in [Vector2(480, 580), Vector2(60, 580)]:
        #     DebugHelper.pauseGame()

        # DebugHelper.drawDashedCircle(pacmanPosition, TILEWIDTH * 5, DebugHelper.RED, 3, 10)
        # DebugHelper.drawDashedCircle(pacmanPosition, TILEWIDTH * 10, DebugHelper.YELLOW, 3, 10)
        # DebugHelper.drawDashedCircle(pacmanPosition, TILEWIDTH * 17, DebugHelper.WHITE, 3, 10)

        # if len(self.last) > 0:
        #     DebugHelper.drawDashedPath(self.last, DebugHelper.GREEN)

        # if mapPos.isInDangerZone:
        #     DebugHelper.drawDangerZone(mapPos.dangerZone)

        if mapPos.isInDangerZone and (mapPos.dangerZone.isDangerous or mapPos.dangerZone.ghostInDangerZone):
            # find the escape path
            edgeMapNode1DangerLevel = obs.calculateDangerLevel(mapPos.dangerZone.edgeMapNodes[0].position)
            edgeMapNode2DangerLevel = obs.calculateDangerLevel(mapPos.dangerZone.edgeMapNodes[1].position)

            if mapPos.dangerZone.ghostInDangerZone:
                edgeMapNodePath1, _ = obs.map.calculateShortestPath(pacmanPosition,
                                                                    mapPos.dangerZone.edgeMapNodes[0].position)
                if obs.isGhostInPath(edgeMapNodePath1):
                    edgeMapNode1DangerLevel = 99999

                edgeMapNodePath2, _ = obs.map.calculateShortestPath(pacmanPosition,
                                                                    mapPos.dangerZone.edgeMapNodes[1].position)
                if obs.isGhostInPath(edgeMapNodePath2):
                    edgeMapNode2DangerLevel = 99999

            if edgeMapNode1DangerLevel < edgeMapNode2DangerLevel:
                escapeTarget = mapPos.dangerZone.edgeMapNodes[0].position
            else:
                escapeTarget = mapPos.dangerZone.edgeMapNodes[1].position

            # DebugHelper.drawDot(escapeTarget, DebugHelper.PURPLE, 12)

            escapePath, _ = obs.map.calculateShortestPath(pacmanPosition, escapeTarget)

            # if obs.isGhostInPath(escapePath):
            #     escapePath = []

            # TODO: this should be closest ghost that is not in freight mode
            closestGhost = obs.getClosestGhost(escapeTarget)
            if closestGhost.mode.current != FREIGHT:
                ghostPath, _ = obs.map.calculateShortestPath(closestGhost.position, escapeTarget, closestGhost)
            else:
                ghostPath = []

            self.last = ghostPath

            # DebugHelper.pauseGame()
            return self.__getDirection__(obs, escapePath[1])

        self.last = []

        # if we are on a node, we can calculate the best direction to go
        if not mapPos.isBetweenMapNodes:
            return self.__getLeastDangerousDirectionFromNode__(obs, obs.map.getClosestMapNode(pacmanPosition))

        # else calculate which of the two directions is the least dangerous
        # ghostBetweenMapNodes = obs.getGhostBetweenMapNodes(mapPos.mapNode1, mapPos.mapNode2)
        # if ghostBetweenMapNodes is not None:
        #     return self.__fleeFromGhost__(obs, ghostBetweenMapNodes, mapPos.isXAxis)
        # else:
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
        pacmanPosition = obs.getPacmanPosition()

        startMapNode, startIsCustom = obs.map.getOrCreateCustomMapNodeOnVector(pacmanPosition)
        # DebugHelper.drawDashedCircle(startMapNode.position, 10, DebugHelper.YELLOW, 5)

        endMapNode1 = obs.map.getEndOfDangerZoneInDirection(startMapNode, LEFT if isXAxis else UP)
        endMapNode2 = obs.map.getEndOfDangerZoneInDirection(startMapNode, RIGHT if isXAxis else DOWN)

        path1, distance1 = obs.map.calculateShortestPath(pacmanPosition, endMapNode1.position)
        path2, distance2 = obs.map.calculateShortestPath(pacmanPosition, endMapNode2.position)

        endMapNode1DangerLevel = obs.calculateDangerLevel(endMapNode1.position)
        endMapNode2DangerLevel = obs.calculateDangerLevel(endMapNode2.position)

        dir1Better = endMapNode1DangerLevel < endMapNode2DangerLevel
        ghostInPath1 = obs.isGhostInPath(path1)
        ghostInPath2 = obs.isGhostInPath(path2)

        if dir1Better and not ghostInPath1:
            return self.__getDirection__(obs, mapNode1.position)
        elif not ghostInPath2:
            return self.__getDirection__(obs, mapNode2.position)
        else:
            return STOP

    def __getLeastDangerousDirectionFromNode__(self, obs: Observation, onMapNode: MapNode) -> int:
        minDangerLevel = 99999
        minDangerDirection = STOP
        for neighborContainer in onMapNode.neighborContainers:
            endMapNode = obs.map.getEndOfDangerZoneInDirection(onMapNode, neighborContainer.direction)

            if endMapNode is None:
                continue

            path, distance = obs.map.calculateShortestPath(neighborContainer.mapNode.position, endMapNode.position)

            distance += manhattanDistance(onMapNode.position, neighborContainer.mapNode.position)

            if obs.isGhostInPath(path):
                continue

            # DebugHelper.drawDashedCircle(endMapNode.position, 10, DebugHelper.PURPLE, 5)
            # DebugHelper.drawDangerLevel(obs, endMapNode.position)

            dangerLevel = obs.calculateDangerLevel(endMapNode.position)
            if dangerLevel < minDangerLevel:
                minDangerLevel = dangerLevel
                minDangerDirection = neighborContainer.direction
        return minDangerDirection

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
