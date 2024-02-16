from __future__ import annotations
import heapq
from typing import List

from PacMaster.utils.utils import manhattanDistance, distanceSquared, isPortalPath, getOppositeDirection, roundVector, \
    directionToString
from Pacman_Complete.constants import *
from Pacman_Complete.ghosts import Ghost
from Pacman_Complete.nodes import NodeGroup, Node
from Pacman_Complete.vector import Vector2


class MapNode(object):
    def __init__(self, node: Node):
        self.node = node

        self.position = roundVector(node.position)
        self.x = self.position.x
        self.y = self.position.y

        self.neighborContainers: List[NeighborContainer] = list()

    def distance_to_nearest_edge(self):
        distance_from_left = self.x
        distance_from_right = 416 - self.x
        distance_from_top = self.y
        distance_from_bottom = 512 - self.y

        return min(distance_from_left, distance_from_right, distance_from_top, distance_from_bottom)

    def __str__(self):
        return f"MapNode{self.position}"

    def __lt__(self, other):
        # Prioritize based on distance to the nearest edge, as nodes closer to any edge are more dangerous
        return self.distance_to_nearest_edge() > other.distance_to_nearest_edge()

    def __eq__(self, other):
        if not isinstance(other, MapNode):
            return NotImplemented

        return self.position == other.position

    def __hash__(self):
        return int(self.x * 10000 + self.y)

    def addNeighbor(self, mapNode: 'MapNode', direction: int, distance: int):
        neighbor = NeighborContainer(mapNode, direction, distance)
        self.neighborContainers.append(neighbor)

    def hasNeighbor(self, mapNode: 'MapNode') -> bool:
        return mapNode in [neighbor.mapNode for neighbor in self.neighborContainers]

    def getNeighbor(self, mapNode: 'MapNode') -> NeighborContainer | None:
        for neighborContainer in self.neighborContainers:
            if neighborContainer.mapNode == mapNode:
                return neighborContainer

        return None

    def getNeighborInDirection(self, direction: int) -> NeighborContainer | None:
        for neighborContainer in self.neighborContainers:
            if neighborContainer.direction == direction:
                return neighborContainer

        return None


class NeighborContainer(object):
    def __init__(self, mapNode: 'MapNode', direction: int, distance: int):
        self.mapNode = mapNode
        self.direction = direction
        self.distance = distance


class DangerZone(object):
    def __init__(self, map: Map, mapPosition: MapPosition):
        self.position = mapPosition.position
        self.midMapNodes = self.__collectMidMapNodes__(mapPosition)
        self.edgeMapNodes = self.__collectEdgeMapNodes()
        self.mapNodes = self.__straightenMapNodes__()

        self.isDangerous, self.dangerousEdgeIndex = self.__isDangerous__(map)

        # if dangerous, find the safer edgeMapNode
        # self.escapeEdgeMapNode = None
        # if self.isDangerous:
        #     for i in range(len(self.edgeMapNodes)):
        #         if i == self.dangerousEdgeIndex:
        #             continue
        #
        #         self.escapeEdgeMapNode = self.edgeMapNodes[i]
        #         break

        self.ghostInDangerZone = self.__isGhostInDangerZone__(map)

    def vectorIsEdgeMapNode(self, vector: Vector2) -> bool:
        for edgeMapNode in self.edgeMapNodes:
            if edgeMapNode.position == vector:
                return True
        return False

    def vectorIsMidMapNode(self, vector: Vector2) -> bool:
        for midMapNode in self.midMapNodes:
            if midMapNode.position == vector:
                return True
        return False

    def __str__(self):
        return (
            f"DangerZone(mapNodes={[str(node) for node in self.mapNodes]}, "
            f"isDangerous={self.isDangerous}, escapeEdgeMapNode={self.escapeEdgeMapNode}, "
            f"edgeMapNodeDangerLevels={self.edgeMapNodeDangerLevels})")

    def __collectMidMapNodes__(self, mapPosition: MapPosition) -> list[MapNode]:
        visited = set()
        dangerZoneMapNodes = []
        queue = []

        if len(mapPosition.mapNode1.neighborContainers) <= 2:
            queue.append(mapPosition.mapNode1)
            visited.add(mapPosition.mapNode1)
            dangerZoneMapNodes.append(mapPosition.mapNode1)

        if mapPosition.mapNode2 is not None:
            if len(mapPosition.mapNode2.neighborContainers) <= 2:
                queue.append(mapPosition.mapNode2)
                visited.add(mapPosition.mapNode2)
                dangerZoneMapNodes.append(mapPosition.mapNode2)

        # flood fill danger zone
        while queue:
            currentMapNode = queue.pop(0)

            for neighbor in currentMapNode.neighborContainers:
                if (len(neighbor.mapNode.neighborContainers) <= 2 and
                        neighbor.mapNode not in visited):
                    queue.append(neighbor.mapNode)

                    dangerZoneMapNodes.append(neighbor.mapNode)
                    visited.add(neighbor.mapNode)

        return dangerZoneMapNodes

    def __collectEdgeMapNodes(self) -> list[MapNode]:
        edgeMapNodes = []

        for mapNode in self.midMapNodes:
            for neighbor in mapNode.neighborContainers:
                if neighbor.mapNode not in self.midMapNodes:
                    edgeMapNodes.append(neighbor.mapNode)

        return edgeMapNodes

    def __straightenMapNodes__(self) -> list[MapNode]:
        straightenedMapNodes = [self.edgeMapNodes[0]]

        finalArrayLength = len(self.edgeMapNodes) + len(self.midMapNodes) - 1
        for i in range(finalArrayLength):
            currentMapNode = straightenedMapNodes[-1]
            for neighborContainer in currentMapNode.neighborContainers:
                mapNodeIsInDangerZone = neighborContainer.mapNode in self.midMapNodes or neighborContainer.mapNode in self.edgeMapNodes
                if mapNodeIsInDangerZone and neighborContainer.mapNode not in straightenedMapNodes:
                    straightenedMapNodes.append(neighborContainer.mapNode)
                    break

        return straightenedMapNodes

    def __isDangerous__(self, map: Map) -> (bool, int):
        for i in range(len(self.edgeMapNodes)):
            edgeMapNode = self.edgeMapNodes[i]
            pacmanDistance = map.calculateDistance(self.position, edgeMapNode.position)

            minGhostDistance = 99999
            for ghost in map.ghosts:
                if ghost.mode.current == FREIGHT:
                    continue

                ghostDistance = map.calculateGhostDistance(ghost, edgeMapNode.position)

                if ghostDistance == 0:
                    continue

                minGhostDistance = min(minGhostDistance, ghostDistance)

            if pacmanDistance > minGhostDistance:
                return True, i
        return False, -1

    def __isGhostInDangerZone__(self, map: Map) -> bool:
        previousMapNode = None
        for mapNode in self.mapNodes:
            if previousMapNode is not None:
                ghostInDangerZone = map.obs.getGhostBetweenMapNodes(previousMapNode, mapNode)
                if ghostInDangerZone is not None and ghostInDangerZone.mode.current != FREIGHT:
                    return True

            previousMapNode = mapNode
        return False


class MapPosition(object):
    def __init__(self, map: Map, vector: Vector2):
        self.position = vector

        self.mapNode1 = map.getMapNode(vector)
        if self.mapNode1 is None:
            self.mapNode1, self.mapNode2, self.isXAxis = map.getBetweenMapNodes(vector)
            self.isBetweenMapNodes = True
        else:
            self.isBetweenMapNodes = False
            self.mapNode2 = None

        self.isInDangerZone = self.__isInDangerZone__()
        if self.isInDangerZone:
            self.dangerZone = DangerZone(map, self)
        else:
            self.dangerZone = None

    def __isInDangerZone__(self) -> bool:
        if len(self.mapNode1.neighborContainers) <= 2:
            return True
        if self.isBetweenMapNodes:
            if len(self.mapNode2.neighborContainers) <= 2:
                return True
        return False


class Map(object):
    def __init__(self, obs, nodeGroup: NodeGroup, ghosts: list[Ghost]):
        self.obs = obs
        self.mapNodes = [MapNode(node) for node in nodeGroup.nodesLUT.values()]
        self.mapNodeDict = {(node.x, node.y): node for node in self.mapNodes}
        self.ghosts = ghosts

        self.__setNodeNeighbors__()

    def __setNodeNeighbors__(self):
        for currentMapNode in self.mapNodes:
            for neighborDirection, neighborNode in currentMapNode.node.neighbors.items():
                if neighborNode is None:
                    continue

                neighborMapNode = self.getMapNode(neighborNode.position)
                if neighborMapNode is None:
                    raise Exception("No node found for neighbor at position: " + str(neighborNode.position))

                distance = 0
                direction = neighborDirection
                if neighborDirection == PORTAL:
                    if neighborMapNode.position.x == 0:
                        direction = RIGHT
                    else:
                        direction = LEFT
                else:
                    distance = manhattanDistance(currentMapNode.position, neighborMapNode.position)

                currentMapNode.addNeighbor(neighborMapNode, direction, distance)

    def getMapNode(self, vector: Vector2) -> MapNode:
        return self.mapNodeDict.get((vector.x, vector.y), None)

    def getClosestMapNode(self, vector: Vector2, snapToGrid: bool = True) -> MapNode:
        mapNode = self.getMapNode(vector)
        if mapNode is not None:
            return mapNode

        if snapToGrid:
            return min(self.mapNodes, key=lambda node:
            manhattanDistance(node.position, vector) if node.position.x == vector.x or node.position.y == vector.y
            else 99999, default=None)

        return min(self.mapNodes, key=lambda node: distanceSquared(node.position, vector), default=None)

    def getBetweenMapNodes(self, vector: Vector2) -> tuple[MapNode, MapNode, bool] | tuple[None, None, bool]:
        for mapNode in self.mapNodes:
            if mapNode.position.x == vector.x or mapNode.position.y == vector.y:
                for neighbor in mapNode.neighborContainers:
                    if self.isBetweenMapNodes(mapNode, vector, neighbor.mapNode):
                        return mapNode, neighbor.mapNode, mapNode.position.y == vector.y

        return None, None, False

    def isBetweenMapNodes(self, mapNode1: MapNode, betweenVector: Vector2, mapNode2: MapNode) -> bool:
        # skip if it is a portal
        if isPortalPath(mapNode1.position, mapNode2.position):
            return False

        if betweenVector.x == mapNode1.x and betweenVector.x == mapNode2.x and \
                min(mapNode1.y, mapNode2.y) <= betweenVector.y <= max(mapNode1.y, mapNode2.y):
            return True
        if betweenVector.y == mapNode1.y and betweenVector.y == mapNode2.y and \
                min(mapNode1.x, mapNode2.x) <= betweenVector.x <= max(mapNode1.x, mapNode2.x):
            return True

        return False

    def getEndOfDangerZoneInDirection(self, mapNode: MapNode, startDirection: int) -> MapNode | None:
        endNeighborContainer = mapNode.getNeighborInDirection(startDirection)

        if endNeighborContainer is None:
            return mapNode

        while len(endNeighborContainer.mapNode.neighborContainers) == 2:
            endMapNode = endNeighborContainer.mapNode

            oppositeDirection = endNeighborContainer.direction * -1
            if endMapNode.neighborContainers[0].direction == oppositeDirection:
                endNeighborContainer = endMapNode.neighborContainers[1]
            else:
                endNeighborContainer = endMapNode.neighborContainers[0]
        return endNeighborContainer.mapNode

    def getOrCreateCustomMapNodeOnVector(self, vector: Vector2,
                                             ghost: Ghost = None) -> (MapNode, bool):
        isGhost = ghost is not None

        vector = roundVector(vector)
        mapNode = self.getMapNode(vector)

        customMapNodeForGhostIsNeeded = isGhost and mapNode is not None and ghost.target.position != mapNode.position

        # create custom MapNode
        if mapNode is None or customMapNodeForGhostIsNeeded:
            customMapNode = MapNode(Node(vector.x, vector.y))

            if customMapNodeForGhostIsNeeded:
                neighborContainer = mapNode.getNeighborInDirection(ghost.direction)
                customMapNode.addNeighbor(neighborContainer.mapNode, ghost.direction,
                                          manhattanDistance(customMapNode.position, neighborContainer.mapNode.position))

                return customMapNode, True
            else:
                startMapNodeA, startMapNodeB, isXAxis = self.getBetweenMapNodes(vector)

            if startMapNodeA is not None:
                if isXAxis:
                    customMapNode.addNeighbor(startMapNodeA, LEFT,
                                              manhattanDistance(customMapNode.position, startMapNodeA.position))
                    customMapNode.addNeighbor(startMapNodeB, RIGHT,
                                              manhattanDistance(customMapNode.position, startMapNodeB.position))
                else:
                    customMapNode.addNeighbor(startMapNodeA, UP,
                                              manhattanDistance(customMapNode.position, startMapNodeA.position))
                    customMapNode.addNeighbor(startMapNodeB, DOWN,
                                              manhattanDistance(customMapNode.position, startMapNodeB.position))
            else:
                customMapNode = self.getClosestMapNode(vector, snapToGrid=False)
            return customMapNode, True
        else:
            return mapNode, False

    def calculateShortestPath(self, startVector: Vector2, endVector: Vector2,
                              ghost: Ghost = None) -> (list[Vector2], int) | (None, None):
        isGhost = ghost is not None

        startMapNode, startIsCustom = self.getOrCreateCustomMapNodeOnVector(startVector, ghost)

        # fix bug when target is at the corners of the map, when the ghosts are in SCATTER mode
        if isGhost and (endVector.x == 0 and endVector.y == 0 or
                        endVector.x == 560 and endVector.y == 0 or
                        endVector.x == 560 and endVector.y == 720 or
                        endVector.x == 0 and endVector.y == 720):
            endMapNode = self.getClosestMapNode(endVector, snapToGrid=False)
            endIsCustom = False
        else:
            endMapNode, endIsCustom = self.getOrCreateCustomMapNodeOnVector(endVector)

        startMapNodeDistance = manhattanDistance(startMapNode.position, startVector)
        endMapNodeDistance = manhattanDistance(endMapNode.position, endVector)

        oppositeDirection = STOP

        # Priority queue: elements are tuples (distance, MapNode)
        priorityQueue = [(startMapNodeDistance, startMapNode)]
        # Dictionary to keep track of the shortest known distance to a node
        distances = {startMapNode: startMapNodeDistance}
        # Dictionary to store the shortest path leading to a node
        previousNodes = {startMapNode: None}
        # Dictionary to store the direction from which a node was reached
        fromDirections = {}
        if isGhost:
            fromDirections[startMapNode] = ghost.direction

        while priorityQueue:
            currentDistance, currentNode = heapq.heappop(priorityQueue)

            # Stop if the end node is reached
            if currentNode == endMapNode:
                break

            # get opposite direction if isGhost, as ghosts cannot turn around 180 degrees
            if isGhost:
                oppositeDirection = getOppositeDirection(fromDirections[currentNode])

            # Explore neighbors
            for neighborContainer in currentNode.neighborContainers:
                # skip if isGhost and neighbor is in opposite direction (ghosts can't 180)
                if isGhost and neighborContainer.direction == oppositeDirection:
                    continue

                distance = currentDistance + neighborContainer.distance
                if neighborContainer.mapNode not in distances or distance < distances[neighborContainer.mapNode]:
                    previousNodes[neighborContainer.mapNode] = currentNode
                    distances[neighborContainer.mapNode] = distance
                    fromDirections[neighborContainer.mapNode] = neighborContainer.direction

                    heapq.heappush(priorityQueue, (distance, neighborContainer.mapNode))

            # is currentMapNode is next to endMapNode, add EndMapNode to PriorityQueue
            # only if end is custom, as then it is not a neighbor to any of the standard nodes
            if endIsCustom and currentNode.hasNeighbor(endMapNode):
                distance = currentDistance + endMapNodeDistance
                if endMapNode not in distances or distance < distances[endMapNode]:
                    previousNodes[endMapNode] = currentNode
                    distances[endMapNode] = distance
                    fromDirections[endMapNode] = getOppositeDirection(endMapNode.getNeighbor(currentNode).direction)

                    heapq.heappush(priorityQueue, (distance, endMapNode))

        if endMapNode not in previousNodes.keys():
            return [], 0
            # raise Exception("No path found between:" +
            #                 " startVector: " + str(startVector) + " startNode: " + str(startMapNode) +
            #                 " endVector: " + str(endVector) + " endNode: " + str(endMapNode))

        # Reconstruct the shortest path
        path = []
        currentNode = endMapNode

        while currentNode:
            path.insert(0, currentNode.position)
            currentNode = previousNodes[currentNode]

        if path[0] == startMapNode:
            return path, int(distances[endMapNode])
        else:
            raise Exception("No path found between " + str(startVector) + " and " + str(endVector))

    def calculateGhostPath(self, ghost: Ghost, endVector: Vector2) -> (list[Vector2], int) | (None, None):
        ghostPosition = ghost.position
        if ghost.overshotTarget():
            ghostPosition = ghost.target.position

        return self.calculateShortestPath(ghostPosition, endVector, ghost)

    def calculateGhostDistance(self, ghost: Ghost, endVector: Vector2) -> (list[Vector2], int) | (None, None):
        ghostPosition = ghost.position
        if ghost.overshotTarget():
            ghostPosition = ghost.target.position

        return self.calculateShortestPath(ghostPosition, endVector, ghost)[1]

    def calculateDistance(self, startVector: Vector2, endVector: Vector2) -> int:
        return self.calculateShortestPath(startVector, endVector)[1]

    def createMapPosition(self, vector: Vector2) -> MapPosition:
        return MapPosition(self, vector)
