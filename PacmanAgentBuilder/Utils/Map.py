from __future__ import annotations
import heapq
from collections import deque
from typing import List

from PacmanAgentBuilder.Utils.utils import manhattanDistance, squaredDistance, isPortalPath, getOppositeDirection, \
    roundVector, distanceToNearestEdge, isInCenterArea
from Pacman_Complete.constants import *
from Pacman_Complete.ghosts import Ghost
from Pacman_Complete.nodes import NodeGroup, Node
from Pacman_Complete.pellets import PelletGroup
from Pacman_Complete.vector import Vector2


class MapNode(object):
    """
    A MapNode represents a node on the map.
    """

    def __init__(self, node: Node):
        self.node = node

        self.position = roundVector(node.position)
        self.x = self.position.x
        self.y = self.position.y

        self.neighborContainers: List[NeighborContainer] = list()

    def addNeighbor(self, mapNode: 'MapNode', direction: int, distance: int):
        """
        Add a neighbor to the MapNode.
        :param mapNode: The neighbor MapNode
        :param direction: The direction to the neighbor
        :param distance: The distance to the neighbor
        :return: None
        """
        neighbor = NeighborContainer(mapNode, direction, distance)
        self.neighborContainers.append(neighbor)

    def hasNeighbor(self, mapNode: 'MapNode') -> bool:
        """
        Check if the MapNode has a specific neighbor.
        :param mapNode: The neighbor MapNode
        :return: True if the MapNode has the neighbor, else False
        """
        return mapNode in [neighbor.mapNode for neighbor in self.neighborContainers]

    def getNeighbor(self, mapNode: 'MapNode') -> NeighborContainer | None:
        """
        Get the NeighborContainer for a specific neighbor.
        :param mapNode: The neighbor MapNode
        :return: The NeighborContainer if the MapNode has the neighbor, else None
        """
        for neighborContainer in self.neighborContainers:
            if neighborContainer.mapNode == mapNode:
                return neighborContainer

        return None

    def getNeighborInDirection(self, direction: int) -> NeighborContainer | None:
        """
        Get the NeighborContainer in a specific direction.
        :param direction: The direction to the neighbor
        :return: The NeighborContainer if the MapNode has the neighbor in the direction, else None
        """
        for neighborContainer in self.neighborContainers:
            if neighborContainer.direction == direction:
                return neighborContainer

        return None

    def __str__(self):
        return f"MapNode{self.position}"

    def __lt__(self, other):
        # Prioritize based on distance to the nearest edge, as nodes closer to any edge are more dangerous
        return distanceToNearestEdge(self.position) > distanceToNearestEdge(other.position)

    def __eq__(self, other):
        if not isinstance(other, MapNode):
            return NotImplemented

        return self.position == other.position

    def __hash__(self):
        return int(self.x * 10000 + self.y)


class NeighborContainer(object):
    """
    A NeighborContainer represents a neighbor to a MapNode.
    It contains the neighbor MapNode, the direction and the distance to the neighbor.
    """

    def __init__(self, mapNode: 'MapNode', direction: int, distance: int):
        self.mapNode = mapNode
        self.direction = direction
        self.distance = distance


class DangerZone(object):
    """
    A ShowIsInDanger represents a zone on the map where the pacman is in danger.
    TODO: add explanation
    """

    def __init__(self, map: Map, mapPosition: MapPosition):
        self.position = mapPosition.position
        self.midMapNodes = self.__collectMidMapNodes__(mapPosition)
        self.edgeMapNodes = self.__collectEdgeMapNodes__()
        self.mapNodes = self.__straightenMapNodes__()

        self.ghostInDangerZone = self.__isGhostInDangerZone__(map)

    def vectorIsEdgeMapNode(self, vector: Vector2) -> bool:
        """
        Check if a vector is an edge MapNode (edge of the ShowIsInDanger).
        :param vector: The vector to check
        :return: True if the vector is an edge MapNode, else False
        """
        for edgeMapNode in self.edgeMapNodes:
            if edgeMapNode.position == vector:
                return True
        return False

    def vectorIsMidMapNode(self, vector: Vector2) -> bool:
        """
        Check if a vector is a mid MapNode (not edge of the ShowIsInDanger).
        :param vector: The vector to check
        :return: True if the vector is a mid MapNode, else False
        """
        for midMapNode in self.midMapNodes:
            if midMapNode.position == vector:
                return True
        return False

    def __str__(self):
        return (
            f"ShowIsInDanger(mapNodes={[str(node) for node in self.mapNodes]})")

    def __collectMidMapNodes__(self, mapPosition: MapPosition) -> list[MapNode]:
        """
        Collect the mid MapNodes of the ShowIsInDanger.
        :param mapPosition: The MapPosition of pacman
        :return: A list of mid MapNodes
        """
        visited = set()
        dangerZoneMapNodes = []
        queue = deque([])

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
            currentMapNode = queue.popleft()

            for neighbor in currentMapNode.neighborContainers:
                if (len(neighbor.mapNode.neighborContainers) <= 2 and
                        neighbor.mapNode not in visited):
                    queue.append(neighbor.mapNode)

                    dangerZoneMapNodes.append(neighbor.mapNode)
                    visited.add(neighbor.mapNode)

        return dangerZoneMapNodes

    def __collectEdgeMapNodes__(self) -> list[MapNode]:
        """
        Collect the edge MapNodes of the ShowIsInDanger.
        :return: A list of the edge MapNodes
        """
        edgeMapNodes = []

        for mapNode in self.midMapNodes:
            for neighbor in mapNode.neighborContainers:
                if neighbor.mapNode not in self.midMapNodes:
                    edgeMapNodes.append(neighbor.mapNode)

        return edgeMapNodes

    def __straightenMapNodes__(self) -> list[MapNode]:
        """
        makes the order of the list of mapNodes match the order of the ShowIsInDanger (the 2 edges at each end of the list)
        :return: A straightened list of MapNodes
        """
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

    def __isGhostInDangerZone__(self, map: Map) -> bool:
        """
        Check if a ghost is in the ShowIsInDanger.
        :param map: The Map object of the current level
        :return: True if a ghost is in the ShowIsInDanger, else False
        """
        previousMapNode = None
        for mapNode in self.mapNodes:
            if previousMapNode is not None:
                ghostInDangerZone = map.obs.getGhostBetweenMapNodes(previousMapNode, mapNode)
                if ghostInDangerZone is not None and ghostInDangerZone.mode.current != FREIGHT:
                    return True

            previousMapNode = mapNode
        return False


class MapPosition(object):
    """
    A MapPosition represents a position on the map.
    It contains information about the position and how the position relates to the map.
    Stuff like if the position is between 2 MapNode or is on a MapNode, if it is in a ShowIsInDanger
    """

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
        """
        Check if the MapPosition is in a ShowIsInDanger.
        :return: True if the MapPosition is in a ShowIsInDanger, else False
        """
        if len(self.mapNode1.neighborContainers) <= 2:
            return True
        if self.isBetweenMapNodes:
            if len(self.mapNode2.neighborContainers) <= 2:
                return True
        return False


class Map(object):
    """
    A Map represents the graph of the current level.
    It is created from the NodeGroup and the Ghosts of the game.
    """

    def __init__(self, obs, nodeGroup: NodeGroup):
        self.obs = obs

        self.mapNodes = []
        for node in nodeGroup.nodesLUT.values():
            if isInCenterArea(node.position):
                continue
            self.mapNodes.append(MapNode(node))

        self.mapNodeDict = {(node.x, node.y): node for node in self.mapNodes}

        self.__setNodeNeighbors__()

        # remove unwanted mapNode at (270,280)
        # TODO why did I do this?
        unwantedVector = Vector2(270, 280)
        for currentMapNode in self.mapNodes:
            if currentMapNode.position == unwantedVector:
                self.mapNodes.remove(currentMapNode)
                break

            for neighborContainer in currentMapNode.neighborContainers:
                if neighborContainer.mapNode.position == unwantedVector:
                    nextNeighborContainer = neighborContainer.mapNode.getNeighborInDirection(
                        neighborContainer.direction)
                    if nextNeighborContainer is not None:
                        totalDistance = neighborContainer.distance + nextNeighborContainer.distance

                        neighborContainer.distance = totalDistance
                        neighborContainer.mapNode = nextNeighborContainer.mapNode

    def __setNodeNeighbors__(self):
        """
        Connect the MapNodes by setting the neighbors of the MapNodes.
        :return: None
        """
        for currentMapNode in self.mapNodes:
            for neighborDirection, neighborNode in currentMapNode.node.neighbors.items():
                if neighborNode is None:
                    continue

                # skip if neighbor is in the center (ghost start area)
                if isInCenterArea(neighborNode.position):
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
        """
        Get the MapNode at a specific vector.
        :param vector: The vector to get the MapNode from
        :return: The MapNode if it exists, else None
        """
        return self.mapNodeDict.get((vector.x, vector.y), None)

    def getNearestMapNode(self, vector: Vector2, snapToGrid: bool = True) -> MapNode:
        """
        Get the nearest MapNode to a specific vector.
        :param vector: The vector to get the nearest MapNode from
        :param snapToGrid: If True, the nearest MapNode has to be in line with the specified vector.
        :return: The nearest MapNode if it exists, else None
        """
        mapNode = self.getMapNode(vector)
        if mapNode is not None:
            return mapNode

        if snapToGrid:
            return min(self.mapNodes, key=lambda node:
            manhattanDistance(node.position, vector) if node.position.x == vector.x or node.position.y == vector.y
            else 99999, default=None)

        return min(self.mapNodes, key=lambda node: squaredDistance(node.position, vector), default=None)

    def getBetweenMapNodes(self, vector: Vector2) -> tuple[MapNode, MapNode, bool] | tuple[None, None, bool]:
        for mapNode in self.mapNodes:
            if mapNode.position.x == vector.x or mapNode.position.y == vector.y:
                for neighbor in mapNode.neighborContainers:
                    if self.isBetweenMapNodes(mapNode, vector, neighbor.mapNode):
                        return mapNode, neighbor.mapNode, mapNode.position.y == vector.y

        return None, None, False

    def isBetweenMapNodes(self, mapNode1: MapNode, betweenVector: Vector2, mapNode2: MapNode) -> bool:
        """
        Check if a vector is between two MapNodes.
        :param mapNode1: The first MapNode
        :param betweenVector: The vector to check
        :param mapNode2: The second MapNode
        :return: True if the vector is between the MapNodes, else False
        """
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

    def getPathToEndOfDangerZoneInDirection(self, mapNode: MapNode, startDirection: int) -> (MapNode, list, int) | (
            None, None, None):
        """
        Get the path to the end of a ShowIsInDanger in a specific direction.
        :param mapNode: The MapNode to start from
        :param startDirection: The direction to go
        :return: The end MapNode, the path and the distance if a path is found, else None, None, None
        """
        endNeighborContainer = mapNode.getNeighborInDirection(startDirection)

        if endNeighborContainer is None:
            return None, [], 0

        path = [mapNode.position]
        distance = manhattanDistance(mapNode.position, endNeighborContainer.mapNode.position)

        # traverse the danger zone to the end in the start direction
        while True:
            path.append(endNeighborContainer.mapNode.position)

            if len(endNeighborContainer.mapNode.neighborContainers) != 2:
                break

            endMapNode = endNeighborContainer.mapNode

            oppositeDirection = endNeighborContainer.direction * -1
            if endMapNode.neighborContainers[0].direction == oppositeDirection:
                endNeighborContainer = endMapNode.neighborContainers[1]
            else:
                endNeighborContainer = endMapNode.neighborContainers[0]

            distance += manhattanDistance(endMapNode.position, endNeighborContainer.mapNode.position)

        path.append(endNeighborContainer.mapNode.position)

        return endNeighborContainer.mapNode, path, distance

    def getEndOfDangerZoneInDirection(self, mapNode: MapNode, startDirection: int) -> MapNode | None:
        """
        Get the end MapNode of a ShowIsInDanger in a specific direction.
        :param mapNode: The MapNode to start from
        :param startDirection: The direction to go
        :return: The end MapNode if found, else None
        """
        endNeighborContainer = mapNode.getNeighborInDirection(startDirection)

        if endNeighborContainer is None:
            return mapNode

        # traverse the danger zone to the end in the start direction
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
        """
        Get MapNode vector is on, else create a new custom MapNode on a specific vector.
        The custom MapNode with have neighbors to the nearest MapNodes in the map/graph.
        :param vector: The vector to get the MapNode from
        :param ghost: If the MapNode is for a ghost, else None
        :return: The MapNode and a boolean if the MapNode is custom
        """
        isGhost = ghost is not None

        vector = roundVector(vector)
        mapNode = self.getMapNode(vector)

        customMapNodeForGhostIsNeeded = isGhost and mapNode is not None and ghost.target.position != mapNode.position

        # create custom MapNode
        if mapNode is None or customMapNodeForGhostIsNeeded:
            customMapNode = MapNode(Node(vector.x, vector.y))

            if customMapNodeForGhostIsNeeded:
                neighborContainer = mapNode.getNeighborInDirection(ghost.direction)

                if neighborContainer is not None:
                    customMapNode.addNeighbor(neighborContainer.mapNode, ghost.direction,
                                              manhattanDistance(customMapNode.position,
                                                                neighborContainer.mapNode.position))

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
                customMapNode = self.getNearestMapNode(vector, snapToGrid=False)
            return customMapNode, True
        else:
            return mapNode, False

    def calculateShortestPath(self, startVector: Vector2, endVector: Vector2,
                              ghost: Ghost = None) -> (list[Vector2], int) | (None, None):
        """
        Calculate the shortest path between two vectors on the map.
        It uses Dijkstra's algorithm with ghost accurate path finding (ghosts can't reverse or go 180)
        :param startVector: The start vector
        :param endVector: The end vector
        :param ghost: if the path is for a ghost, else None
        :return: The shortest path and the distance if a path is found, else None, None
        """
        isGhost = ghost is not None

        if isGhost and isInCenterArea(startVector):
            return [], 0

        startMapNode, startIsCustom = self.getOrCreateCustomMapNodeOnVector(startVector, ghost)

        # fix bug when ghosts' target is at the corners of the map, when the ghosts are in SCATTER mode
        if isGhost and (endVector.x == 0 and endVector.y == 0 or
                        endVector.x == 560 and endVector.y == 0 or
                        endVector.x == 560 and endVector.y == 720 or
                        endVector.x == 0 and endVector.y == 720):
            endMapNode = self.getNearestMapNode(endVector, snapToGrid=False)
            endIsCustom = False
        else:
            endMapNode, endIsCustom = self.getOrCreateCustomMapNodeOnVector(endVector)

        # calculate the distance to the start and end MapNodes.
        startMapNodeDistance = manhattanDistance(startMapNode.position, startVector)  # + aStarHeuristic
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

        # return empty path and 0 distance if no path is found
        if endMapNode not in previousNodes.keys():
            return [], 0

        # reconstruct path
        path = []
        currentNode = endMapNode
        while currentNode:
            path.insert(0, currentNode.position)
            currentNode = previousNodes[currentNode]

        return path, int(distances[endMapNode])
        # TODO remove this if it works without
        # if path[0] == startMapNode:
        #     return path, int(distances[endMapNode])
        # else:
        #     raise Exception("No path found between " + str(startVector) + " and " + str(endVector))

    def calculateGhostPath(self, ghost: Ghost, endVector: Vector2) -> (list[Vector2], int) | (None, None):
        """
        Calculate the path for a ghost to a specific vector.
        :param ghost: The ghost to calculate the path for
        :param endVector: The vector to calculate the path to
        :return: The path and the distance if a path is found, else None, None
        """
        ghostPosition = ghost.position
        if ghost.overshotTarget():
            ghostPosition = ghost.target.position

        return self.calculateShortestPath(ghostPosition, endVector, ghost)

    def calculateDistance(self, startVector: Vector2, endVector: Vector2) -> int:
        """
        Calculate the distance between two vectors on the map.
        :param startVector: The starting vector
        :param endVector: The ending vector
        :return: The distance between the vectors
        """
        return self.calculateShortestPath(startVector, endVector)[1]

    def createMapPosition(self, vector: Vector2) -> MapPosition:
        """
        Create a MapPosition object for a specific vector.
        This is just to hide the MapPosition constructor.
        :param vector: The vector to create the MapPosition from
        :return: The MapPosition object
        """
        return MapPosition(self, vector)
