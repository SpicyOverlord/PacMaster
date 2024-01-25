from __future__ import annotations
import heapq

from PacMaster.utils.utils import manhattanDistance, distanceSquared
from Pacman_Complete.constants import *
from Pacman_Complete.nodes import NodeGroup, Node
from Pacman_Complete.vector import Vector2


class MapNode(object):
    def __init__(self, node: Node):
        self.node = node

        self.position = node.position
        self.x = node.position.x
        self.y = node.position.y

        self.neighbors = []

    def distance_to_nearest_edge(self):
        distance_from_left = self.x
        distance_from_right = 416 - self.x
        distance_from_top = self.y
        distance_from_bottom = 512 - self.y

        return min(distance_from_left, distance_from_right, distance_from_top, distance_from_bottom)

    def __lt__(self, other):
        # Prioritize based on distance to the nearest edge, as nodes closer to any edge are more dangerous
        return self.distance_to_nearest_edge() > other.distance_to_nearest_edge()

    def __eq__(self, other):
        if not isinstance(other, MapNode):
            return NotImplemented

        return self.position == other.position

    def __hash__(self):
        return int(self.x * 10000 + self.y)

    def addNeighbor(self, node: 'MapNode', direction: int, distance: int):
        neighbor = Neighbor(node, direction, distance)
        self.neighbors.append(neighbor)

    def hasNeighbor(self, node: 'MapNode') -> bool:
        return node in [neighbor.mapNode for neighbor in self.neighbors]

    # def getNeighborByDirection(self, direction: int) -> 'Neighbor' | None:
    #     for neighbor in self.neighbors:
    #         if neighbor.direction == direction:
    #             return neighbor
    #
    #     return None


class Neighbor(object):
    def __init__(self, mapNode: 'MapNode', direction: int, distance: int):
        self.mapNode = mapNode
        self.direction = direction
        self.distance = distance


class Map(object):
    def __init__(self, nodeGroup: NodeGroup):
        self.mapNodes = [MapNode(node) for node in nodeGroup.nodesLUT.values()]
        self.mapNodeDict = {(node.x, node.y): node for node in self.mapNodes}

        self.__setNodeNeighbors__()

    def __setNodeNeighbors__(self):
        for mapNode in self.mapNodes:
            for neighborDirection, neighborNode in mapNode.node.neighbors.items():
                if neighborNode is None:
                    continue

                neighborMapNode = self.getOnNode(neighborNode.position)
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
                    distance = manhattanDistance(mapNode.position, neighborMapNode.position)

                mapNode.addNeighbor(neighborMapNode, direction, distance)

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

    def getOnNode(self, vector: Vector2) -> MapNode | None:
        closestMapNode = self.getClosestMapNode(vector)
        closestMapNodeDistance = manhattanDistance(vector, closestMapNode.position)

        if closestMapNodeDistance <= 4:
            return closestMapNode

        return None

    def getBetweenMapNodes(self, vector: Vector2) -> tuple[MapNode, MapNode, bool] | tuple[None, None, bool]:
        for mapNode in self.mapNodes:
            if mapNode.position.x == vector.x or mapNode.position.y == vector.y:
                for neighbor in mapNode.neighbors:
                    if self.isBetweenMapNodes(mapNode.position, vector, neighbor.mapNode.position):
                        return mapNode, neighbor.mapNode, mapNode.position.y == vector.y

        return None, None, False

    def isBetweenMapNodes(self, mapNode1: MapNode, betweenVector: Vector2, mapNode2: MapNode) -> bool:
        if betweenVector.x == mapNode1.x and betweenVector.x == mapNode2.x and \
                min(mapNode1.y, mapNode2.y) <= betweenVector.y <= max(mapNode1.y, mapNode2.y):
            return True
        if betweenVector.y == mapNode1.y and betweenVector.y == mapNode2.y and \
                min(mapNode1.x, mapNode2.x) <= betweenVector.x <= max(mapNode1.x, mapNode2.x):
            return True

        return False

    def getOrCreateCustomMapNodeOnVector(self, vector: Vector2) -> (MapNode, bool):
        mapNode = self.getOnNode(vector)

        if mapNode is None:
            mapNode = MapNode(Node(vector.x, vector.y))
            startMapNodeA, startMapNodeB, isXAxis = self.getBetweenMapNodes(vector)

            if startMapNodeA is not None:
                if isXAxis:
                    mapNode.addNeighbor(startMapNodeA, LEFT,
                                        manhattanDistance(mapNode.position, startMapNodeA.position))
                    mapNode.addNeighbor(startMapNodeB, RIGHT,
                                        manhattanDistance(mapNode.position, startMapNodeB.position))
                else:
                    mapNode.addNeighbor(startMapNodeA, UP, manhattanDistance(mapNode.position, startMapNodeA.position))
                    mapNode.addNeighbor(startMapNodeB, DOWN,
                                        manhattanDistance(mapNode.position, startMapNodeB.position))
            else:
                mapNode = self.getClosestMapNode(vector, snapToGrid=False)
        else:
            return mapNode, False
        return mapNode, True

    def getShortestPath(self, startVector: Vector2, endVector: Vector2) -> (list[Vector2], int) | (None, None):
        startMapNode, startIsCustom = self.getOrCreateCustomMapNodeOnVector(startVector)
        endMapNode, endIsCustom = self.getOrCreateCustomMapNodeOnVector(endVector)

        startMapNodeDistance = manhattanDistance(startMapNode.position, startVector)
        endMapNodeDistance = manhattanDistance(endMapNode.position, endVector)

        # Priority queue: elements are tuples (distance, MapNode)
        priorityQueue = [(startMapNodeDistance, startMapNode)]
        # Dictionary to keep track of the shortest known distance to a node
        distances = {startMapNode: startMapNodeDistance}
        # Dictionary to store the shortest path leading to a node
        previousNodes = {startMapNode: None}

        while priorityQueue:
            current_distance, currentNode = heapq.heappop(priorityQueue)

            # Stop if the end node is reached
            if currentNode == endMapNode:
                break

            # Explore neighbors
            for neighbor in currentNode.neighbors:
                distance = current_distance + neighbor.distance
                if neighbor.mapNode not in distances or distance < distances[neighbor.mapNode]:
                    distances[neighbor.mapNode] = distance
                    previousNodes[neighbor.mapNode] = currentNode
                    heapq.heappush(priorityQueue, (distance, neighbor.mapNode))

            # is currentMapNode is next to endMapNode, add EndMapNode to PriorityQueue
            # only if end is custom, as then it is not a neighbor to any of the standard nodes
            if endIsCustom and endMapNode.hasNeighbor(currentNode):
                distance = current_distance + endMapNodeDistance
                if endMapNode not in distances or distance < distances[endMapNode]:
                    distances[endMapNode] = distance
                    previousNodes[endMapNode] = currentNode
                    heapq.heappush(priorityQueue, (distance, endMapNode))

        # Reconstruct the shortest path

        path = []
        current = endMapNode
        while current:
            path.insert(0, current.position)
            current = previousNodes[current]

        if path[0] == startMapNode:
            return path, int(distances[endMapNode])
        else:
            return None, None
