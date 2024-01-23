from PacMaster.utils.utils import manhattenDistance
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

    def addNeighbor(self, node: 'MapNode', direction: int, distance: int):
        neighbor = Neighbor(node, direction, distance)
        self.neighbors.append(neighbor)

    def isNeighborTo(self, node: 'MapNode'):
        return node in [neighbor.node for neighbor in self.neighbors]


class Neighbor(object):
    def __init__(self, node: 'MapNode', direction: int, distance: int):
        self.node = node
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

                neighborMapNode = self.getClosestMapNode(neighborNode.position)
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
                    distance = manhattenDistance(mapNode.position, neighborMapNode.position)

                mapNode.addNeighbor(neighborMapNode, direction, distance)

    def getClosestMapNode(self, vector: Vector2) -> MapNode:
        mapNode = self.getMapNode(vector)
        if mapNode is not None:
            return mapNode

        return min(self.mapNodes, key=lambda node: manhattenDistance(node.position, vector), default=None)

    def getMapNode(self, vector: Vector2) -> MapNode:
        return self.mapNodeDict.get((vector.x, vector.y), None)
