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

    def addNeighbor(self, node: 'MapNode'):
        self.neighbors.append(node)

    def isNeighborTo(self, node: 'MapNode'):
        return node in self.neighbors


class Map(object):
    def __init__(self, nodeGroup: NodeGroup):
        self.mapNodes = [MapNode(node) for node in nodeGroup.nodesLUT.values()]
        self.mapNodeDict = {(node.x, node.y): node for node in self.mapNodes}

        self.__setNodeNeighbors__()

    def __setNodeNeighbors__(self):
        for mapNode in self.mapNodes:
            for neighborNode in mapNode.node.neighbors.values():
                if neighborNode is None:
                    continue

                neighborMapNode = self.getClosestMapNode(neighborNode.position)
                if neighborMapNode is None:
                    raise Exception("No neighbor found for node at position: " + str(neighborNode.position))

                mapNode.addNeighbor(neighborMapNode)

    def getClosestMapNode(self, vector: Vector2) -> MapNode:
        mapNode = self.mapNodeDict.get((vector.x, vector.y), None)
        if mapNode is not None:
            return mapNode

        return min(self.mapNodes, key=lambda node: manhattenDistance(node.position, vector), default=None)

    def getFromToDirection(self, fromNode: MapNode, toNode: MapNode):
        if not fromNode.isNeighborTo(toNode):
            raise Exception("Nodes are not neighbors")

        if fromNode.x == toNode.x:
            if fromNode.y > toNode.y:
                return UP
            else:
                return DOWN
        else:
            if fromNode.x > toNode.x:
                return LEFT
            else:
                return RIGHT
