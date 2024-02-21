import pygame
from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT

from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.map import MapNode
from PacMaster.utils.observation import Observation
from PacMaster.utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class UntrappableAgent(IAgent):
    def __init__(self, gameController):
        super().__init__(gameController)

    def calculateNextMove(self):
        obs = Observation(self.gameController)
        self.takeStats(obs)

        # key_pressed = pygame.key.get_pressed()
        # if key_pressed[K_UP]:
        #     return UP
        # if key_pressed[K_DOWN]:
        #     return DOWN
        # if key_pressed[K_LEFT]:
        #     return LEFT
        # if key_pressed[K_RIGHT]:
        #     return RIGHT

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

        return self.__getLeastDangerousDirectionFromCustomNode__(obs)

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

            DebugHelper.drawDashedCircle(escapeTarget, 12, DebugHelper.PURPLE, 5)

            escapePath, _ = obs.map.calculateShortestPath(pacmanPosition, escapeTarget)

            # if obs.isGhostInPath(escapePath):
            #     escapePath = []

            # TODO: this should be closest ghost that is not in freight mode
            closestGhost = obs.getClosestGhost(escapeTarget)
            if closestGhost.mode.current != FREIGHT:
                ghostPath, _ = obs.map.calculateShortestPath(closestGhost.position, escapeTarget, closestGhost)
            else:
                ghostPath = []

            # DebugHelper.pauseGame()
            return self.__getDirection__(obs, escapePath[1])

        return self.__getLeastDangerousDirectionFromCustomNode__(obs)

        # # if we are on a node, we can calculate the best direction to go
        # if not mapPos.isBetweenMapNodes:
        #     return self.__getLeastDangerousDirectionFromNode__(obs, obs.map.getClosestMapNode(pacmanPosition))
        #
        # # else calculate which of the two directions is the least dangerous
        # # ghostBetweenMapNodes = obs.getGhostBetweenMapNodes(mapPos.mapNode1, mapPos.mapNode2)
        # # if ghostBetweenMapNodes is not None:
        # #     return self.__fleeFromGhost__(obs, ghostBetweenMapNodes, mapPos.isXAxis)
        # # else:
        # return self.__getLeastDangerousDirection__(obs, mapPos.mapNode1, mapPos.mapNode2, mapPos.isXAxis)

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

    # def __getLeastDangerousDirection__(self, obs: Observation, mapNode1: MapNode, mapNode2: MapNode,
    #                                    isXAxis: bool) -> int:
    #     pacmanPosition = obs.getPacmanPosition()
    #
    #     startMapNode, startIsCustom = obs.map.getOrCreateCustomMapNodeOnVector(pacmanPosition)
    #     # DebugHelper.drawDashedCircle(startMapNode.position, 10, DebugHelper.YELLOW, 5)
    #
    #     endMapNode1, path1, distance1 = obs.map.getPathToEndOfDangerZoneInDirection(startMapNode,
    #                                                                                 LEFT if isXAxis else UP)
    #     endMapNode2, path2, distance2 = obs.map.getPathToEndOfDangerZoneInDirection(startMapNode,
    #                                                                                 RIGHT if isXAxis else DOWN)
    #
    #     endMapNode1DangerLevel = obs.calculateDangerLevel(endMapNode1.position)
    #     endMapNode2DangerLevel = obs.calculateDangerLevel(endMapNode2.position)
    #
    #     dir1Better = endMapNode1DangerLevel < endMapNode2DangerLevel
    #     ghostInPath1 = obs.isGhostInPath(path1)
    #     ghostInPath2 = obs.isGhostInPath(path2)
    #
    #     if dir1Better and not ghostInPath1:
    #         return self.__getDirection__(obs, mapNode1.position)
    #     elif not ghostInPath2:
    #         return self.__getDirection__(obs, mapNode2.position)
    #     else:
    #         return STOP

    # def __getLeastDangerousDirectionFromNode__(self, obs: Observation, onMapNode: MapNode) -> int:
    #     minDangerLevel = 99999
    #     minDangerDirection = STOP
    #     for neighborContainer in onMapNode.neighborContainers:
    #         endMapNode = obs.map.getEndOfDangerZoneInDirection(onMapNode, neighborContainer.direction)
    #
    #         if endMapNode is None:
    #             continue
    #
    #         path, distance = obs.map.calculateShortestPath(neighborContainer.mapNode.position, endMapNode.position)
    #
    #         distance += manhattanDistance(onMapNode.position, neighborContainer.mapNode.position)
    #
    #         if obs.isGhostInPath(path):
    #             DebugHelper.drawPath(path, DebugHelper.RED, 5)
    #             DebugHelper.pauseGame()
    #             continue
    #
    #         DebugHelper.drawPath(path, DebugHelper.GREEN, 5)
    #
    #         # DebugHelper.drawDashedCircle(endMapNode.position, 10, DebugHelper.PURPLE, 5)
    #         # DebugHelper.drawDangerLevel(obs, endMapNode.position)
    #
    #         dangerLevel = obs.calculateDangerLevel(endMapNode.position)
    #         if dangerLevel < minDangerLevel:
    #             minDangerLevel = dangerLevel
    #             minDangerDirection = neighborContainer.direction
    #     return minDangerDirection

    # def __getLeastDangerousDirectionFromCustomNode__(self, obs: Observation) -> int:
    #     startMapNode, startIsCustom = obs.map.getOrCreateCustomMapNodeOnVector(obs.getPacmanPosition())
    #
    #     minDangerLevel = 99999
    #     minDangerDirection = STOP
    #     for neighborContainer in startMapNode.neighborContainers:
    #         endMapNode = obs.map.getEndOfDangerZoneInDirection(startMapNode, neighborContainer.direction)
    #
    #         if endMapNode is None:
    #             continue
    #
    #         path, distance = obs.map.calculateShortestPath(neighborContainer.mapNode.position, endMapNode.position)
    #
    #         distance += manhattanDistance(startMapNode.position, neighborContainer.mapNode.position)
    #
    #         if obs.isGhostInPath(path) or obs.getGhostBetweenMapNodes(startMapNode,
    #                                                                   neighborContainer.mapNode) is not None:
    #             DebugHelper.drawLine(startMapNode.position, neighborContainer.mapNode.position, DebugHelper.PURPLE, 5)
    #             DebugHelper.drawPath(path, DebugHelper.RED, 5)
    #             # DebugHelper.pauseGame()
    #             continue
    #
    #         DebugHelper.drawLine(startMapNode.position, neighborContainer.mapNode.position, DebugHelper.YELLOW, 5)
    #         DebugHelper.drawPath(path, DebugHelper.GREEN, 5)
    #
    #         # DebugHelper.drawDashedCircle(endMapNode.position, 10, DebugHelper.PURPLE, 5)
    #         # DebugHelper.drawDangerLevel(obs, endMapNode.position)
    #
    #         dangerLevel = obs.calculateDangerLevel(endMapNode.position)
    #         if dangerLevel < minDangerLevel:
    #             minDangerLevel = dangerLevel
    #             minDangerDirection = neighborContainer.direction
    #     return minDangerDirection

    def __getLeastDangerousDirectionFromCustomNode__(self, obs: Observation) -> int:
        startMapNode, startIsCustom = obs.map.getOrCreateCustomMapNodeOnVector(obs.getPacmanPosition())

        minDangerLevel = 99999
        minDangerDirection = STOP
        for neighborContainer in startMapNode.neighborContainers:
            endMapNode, path, distance = obs.map.getPathToEndOfDangerZoneInDirection(startMapNode,
                                                                                     neighborContainer.direction)

            if endMapNode is None:
                print("skipping")
                continue

            if obs.isGhostInPath(path):
                DebugHelper.drawPath(path, DebugHelper.RED, 5)
                # DebugHelper.pauseGame()
                continue

            DebugHelper.drawPath(path, DebugHelper.GREEN, 5)

            # DebugHelper.drawDashedCircle(endMapNode.position, 10, DebugHelper.PURPLE, 5)
            # DebugHelper.drawDangerLevel(obs, endMapNode.position)

            dangerLevel = obs.calculateDangerLevel(endMapNode.position)
            if dangerLevel < minDangerLevel:
                minDangerLevel = dangerLevel
                minDangerDirection = neighborContainer.direction
        return minDangerDirection
