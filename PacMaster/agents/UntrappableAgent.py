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

        # DebugHelper.drawMap(obs)
        # DebugHelper.drawDangerLevels(obs)

        # DebugHelper.drawGhostPaths(obs)
        # DebugHelper.pauseGame()

        # testMapNode = obs.map.getMapNode(Vector2(480, 580))
        # self.__getLeastDangerousDirectionFromNode__(obs, testMapNode)
        # DebugHelper.pauseGame()

        pacmanPosition = obs.getPacmanPosition()
        mapPos = obs.map.createMapPosition(pacmanPosition)

        # DebugHelper.drawDashedCircle(pacmanPosition, TILEWIDTH * 5, DebugHelper.RED, 3, 10)
        # DebugHelper.drawDashedCircle(pacmanPosition, TILEWIDTH * 10, DebugHelper.YELLOW, 3, 10)
        # DebugHelper.drawDashedCircle(pacmanPosition, TILEWIDTH * 17, DebugHelper.WHITE, 3, 10)

        if len(self.last) > 0:
            DebugHelper.drawDashedPath(self.last, DebugHelper.GREEN)
        if mapPos.isInDangerZone:
            DebugHelper.drawDangerZone(mapPos.dangerZone)

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

            DebugHelper.drawDot(escapeTarget, DebugHelper.PURPLE, 12)

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
        EndMapNode1 = obs.map.getEndOfDangerZoneInDirection(mapNode1, LEFT if isXAxis else UP)
        EndMapNode2 = obs.map.getEndOfDangerZoneInDirection(mapNode1, RIGHT if isXAxis else DOWN)

        endMapNode1DangerLevel = obs.calculateDangerLevel(EndMapNode1.position)
        endMapNode2DangerLevel = obs.calculateDangerLevel(EndMapNode2.position)
        if endMapNode1DangerLevel < endMapNode2DangerLevel:
            return self.__getDirection__(obs, mapNode1.position)
        elif endMapNode1DangerLevel == endMapNode2DangerLevel:
            return STOP
        else:
            return self.__getDirection__(obs, mapNode2.position)

    # TODO: redo this:
    #  if a neighbor is in a danger zone, we should look at the other edgeMapNode, as it is the target we are moving towards
    #  this makes sure that we don't go into a danger zone where the other exit is shite.
    #  this also makes the agent not only look at direct neighbors, but looks further if there is only one direction to go
    #  -
    #  This should probably be moved to the MapPos class, as the collection, dangerLevel evaluation and ghostInPath
    #  of the paths to the 4 "neighbors" is something we always want to do, and will probably need in future agents
    def __getLeastDangerousDirectionFromNode__(self, obs: Observation, onMapNode: MapNode) -> int:
        # DebugHelper.pauseGame()

        minDangerLevel = 99999
        minDangerDirection = STOP
        for neighborContainer in onMapNode.neighborContainers:
            endMapNode = obs.map.getEndOfDangerZoneInDirection(onMapNode, neighborContainer.direction)

            path, distance = obs.map.calculateShortestPath(onMapNode.position, endMapNode.position)

            if obs.isGhostInPath(path):
                continue

            DebugHelper.drawDot(endMapNode.position, DebugHelper.PURPLE, 5)
            DebugHelper.drawDangerLevel(obs, endMapNode.position)

            dangerLevel = obs.calculateDangerLevel(endMapNode.position)
            if dangerLevel < minDangerLevel:
                minDangerLevel = dangerLevel
                minDangerDirection = neighborContainer.direction
        return minDangerDirection

            # endNeighborContainer = neighborContainer
            # while len(endNeighborContainer.mapNode.neighborContainers) == 2:
            #     endMapNode = endNeighborContainer.mapNode
            #
            #     oppositeDirection = endNeighborContainer.direction * -1
            #     if endMapNode.neighborContainers[0].direction == oppositeDirection:
            #         endNeighborContainer = endMapNode.neighborContainers[1]
            #     else:
            #         endNeighborContainer = endMapNode.neighborContainers[0]
            #
            # DebugHelper.drawDot(endNeighborContainer.mapNode.position, DebugHelper.PURPLE, 5)

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
