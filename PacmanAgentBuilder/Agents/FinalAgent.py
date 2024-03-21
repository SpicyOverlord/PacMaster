from collections import deque

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.Map import MapPosition
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class FinalAgent(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

    def calculateNextMove(self, obs: Observation):
        mapPos = obs.map.createMapPosition(obs.getPacmanPosition())
        # sleep(0.03)
        # DebugHelper.drawMap(obs)
        # DebugHelper.drawDangerZone(mapPos.dangerZone)

        # if in danger, flee
        if self.isInDanger(obs, mapPos):
            return self.flee(obs, mapPos)

        # else, collect pellets
        return self.collect(obs)

    def isInDanger(self, obs: Observation, mapPos: MapPosition) -> bool:
        dangerLevel = self.calculateDangerLevel(obs, mapPos, mapPos.mapNode1.position, self.weightContainer)
        if mapPos.isBetweenMapNodes:
            dangerLevel = max(
                dangerLevel,
                self.calculateDangerLevel(obs, mapPos, mapPos.mapNode2.position, self.weightContainer)
            )

        return dangerLevel > self.weightContainer.get('fleeThreshold')

    def flee(self, obs: Observation, mapPos: MapPosition) -> int:
        startMapNode, startIsCustom = obs.map.getOrCreateCustomMapNodeOnVector(obs.getPacmanPosition())

        minDangerLevel = 99999
        minDangerDirection = STOP
        for neighborContainer in startMapNode.neighborContainers:
            endMapNode, path, distance = obs.map.getPathToEndOfDangerZoneInDirection(startMapNode,
                                                                                     neighborContainer.direction)

            if obs.isGhostInPath(path):
                # DebugHelper.drawPath(path, DebugHelper.RED, 5)
                continue
            # DebugHelper.drawPath(path, DebugHelper.GREEN, 5)

            dangerLevel = self.calculateDangerLevel(obs, mapPos, endMapNode.position, self.weightContainer)
            # DebugHelper.drawDangerLevel(dangerLevel, endMapNode.position)

            if dangerLevel < minDangerLevel:
                minDangerLevel = dangerLevel
                minDangerDirection = neighborContainer.direction

        return minDangerDirection

    def collect(self, obs: Observation):
        pacmanPosition = obs.getPacmanPosition()

        nextPos = self.calculateTargetPelletPosition(obs)
        nextPosMapPosition = obs.map.createMapPosition(nextPos)
        # DebugHelper.drawDot(nextPos, 3, DebugHelper.RED)

        paths = [
            obs.map.calculateShortestPath(pacmanPosition, nextPosMapPosition.mapNode1.position),
            obs.map.calculateShortestPath(pacmanPosition, nextPosMapPosition.mapNode2.position)
            if nextPosMapPosition.isBetweenMapNodes else (None, float('inf'))
        ]

        # Prefer path that includes nextPos and has the shortest distance
        preferred_path, preferred_distance = None, float('inf')

        for path, distance in paths:
            if path and obs.isVectorInPath(path, nextPos) and (preferred_path is None or distance < preferred_distance):
                preferred_path, preferred_distance = path, distance

        # If no path includes nextPos or if both paths have been calculated and neither includes nextPos,
        # choose the shorter path
        if preferred_path is None:
            preferred_path, preferred_distance = min(paths, key=lambda x: x[1])

        # Draw the preferred path and return direction of the second point
        if preferred_path and len(preferred_path) > 1:
            # DebugHelper.drawPath(preferred_path, DebugHelper.YELLOW, 10)
            return self.getDirection(obs, preferred_path[1])
        else:
            # If there is no path or the path doesn't have a second point, move towards nextPos directly
            return self.getDirection(obs, nextPos)

    def calculateTargetPelletPosition(self, obs: Observation):
        pelletPositions = obs.getPelletPositions()
        pelletIslandDistance = self.weightContainer.get('PelletIslandDistance')

        # colors = [DebugHelper.GREEN, DebugHelper.RED, DebugHelper.BLUE, DebugHelper.YELLOW,
        #           DebugHelper.PURPLE, DebugHelper.LIGHTBLUE]

        visited = set()
        islands = []
        for pelletPosition in pelletPositions:
            if pelletPosition in visited:
                continue

            island = []
            queue = deque([pelletPosition])
            while queue:
                current = queue.popleft()

                if current in visited:
                    continue

                visited.add(current)
                island.append(current)

                for pelletPosition2 in pelletPositions:
                    if (abs(current.x - pelletPosition2.x) < pelletIslandDistance and
                            abs(current.y - pelletPosition2.y) < pelletIslandDistance):

                        if pelletPosition2 in visited:
                            continue

                        queue.append(pelletPosition2)

            islands.append(island)

        # calculate the distance to each island
        pacmanPosition = obs.getPacmanPosition()
        islandDistances = []
        closestIslandPositions = []
        for i, island in enumerate(islands):
            minDistance = 999999
            minPosition = None
            for position in island:
                distance = manhattanDistance(pacmanPosition, position)
                if distance < minDistance:
                    minDistance = distance
                    minPosition = position

            islandDistances.append(minDistance)
            closestIslandPositions.append(minPosition)

        # find island with the highest value
        bestIslandValue = 0
        bestIslandIndex = 0
        islandSizeMultiplier = self.weightContainer.get('IslandSizeMultiplier')
        islandDistanceMultiplier = self.weightContainer.get('IslandDistanceMultiplier')
        for i, island in enumerate(islands):
            islandValue = (islandSizeMultiplier / (len(island) + 1)) * (
                    islandDistanceMultiplier / (islandDistances[i] + 1))

            if islandValue > bestIslandValue:
                bestIslandValue = islandValue
                bestIslandIndex = i

        # # draw highlight for the best island
        # for position in islands[bestIslandIndex]:
        #     DebugHelper.drawDot(position, 5, DebugHelper.WHITE)
        # # draw all islands in different colors
        # for i, island in enumerate(islands):
        #     for position in island:
        #         DebugHelper.drawDot(position, 4, colors[i % 6])

        return closestIslandPositions[bestIslandIndex]

    def calculateDangerLevel(self, obs: Observation, mapPos: MapPosition,
                             vector: Vector2, weights: WeightContainer) -> float:

        minGhostDistance = 9999999
        totalGhostDistance = 0.0
        ghostsDangerValue = 0.0
        numberOfCloseGhosts = 0

        for ghost in obs.getGhosts():
            # ignore ghost if it is not dangerous
            if ghost.mode.current in (FREIGHT, SPAWN) or isInCenterArea(ghost.position):
                continue

            ghostPath, ghostDistance = obs.map.calculateGhostPath(ghost=ghost, endVector=vector)

            # ignore ghost if it can't reach position (this normally only happens if the ghost is in the start area)
            if len(ghostPath) == 0:
                continue

            minGhostDistance = min(minGhostDistance, ghostDistance)

            # Threshold distance for a ghost to be considered 'too far away' to be considered
            if ghostDistance > weights.get('tooFarAwayThreshold'):
                continue

            totalGhostDistance += ghostDistance

            # Threshold distance for a ghost to be considered 'close'
            if ghostDistance < weights.get('tooCloseThreshold'):
                numberOfCloseGhosts += 1

            # for each ghost, calculate the 'ghost danger value' for that ghost based on its distance and weight
            ghostWeight = 0
            if ghost.name == BLINKY:
                ghostWeight = weights.get('blinky')
            elif ghost.name == PINKY:
                ghostWeight = weights.get('pinky')
            elif ghost.name == INKY:
                ghostWeight = weights.get('inky')
            elif ghost.name == CLYDE:
                ghostWeight = weights.get('clyde')
            ghostsDangerValue += ((1 + ghostWeight) * weights.get('ghostMultiplier')) / (1 + ghostDistance)

        # Calculate pellet level (basically how many pellets are around the position)
        minPelletDistance = 99999
        totalPelletDistance = 1.0
        for pelletPosition in obs.getPelletPositions():
            pelletDistance = manhattanDistance(pelletPosition, vector)
            if pelletDistance < weights.get('pelletLevelDistanceInDangerLevel'):
                totalPelletDistance += pelletDistance
                if pelletDistance < minPelletDistance:
                    minPelletDistance = pelletDistance
        for powerPelletPosition in obs.getPowerPelletPositions():
            pelletDistance = manhattanDistance(powerPelletPosition, vector)
            if pelletDistance < weights.get('pelletLevelDistanceInDangerLevel'):
                totalPelletDistance += pelletDistance
                if pelletDistance < minPelletDistance:
                    minPelletDistance = pelletDistance
        pelletLevel = totalPelletDistance / (minPelletDistance + 1) * 0.001 * weights.get(
            'pelletsInDangerLevelMultiplier')

        # distance to pacman
        distanceToPacman = manhattanDistance(vector, obs.getPacmanPosition()) * 0.001 * weights.get(
            'distanceToPacManMultiplier')
        # Adjust danger level based on the closest ghost
        closestGhostValue = (1 / (minGhostDistance + 1)) * 1000
        # Further adjust based on the number of close ghosts
        closeGhostValue = numberOfCloseGhosts * weights.get('tooCloseValue')

        # Calculate danger level (minus pellet level to make pacman flee towards pellets)
        dangerLevel = closestGhostValue + closeGhostValue + ghostsDangerValue + distanceToPacman - pelletLevel
        # print(
        #     f"danger: {dangerLevel}, "
        #     f"Closest ghost value: {closestGhostValue}, "
        #     f"close ghost value: {closeGhostValue}, "
        #     f"ghost danger value: {ghostsDangerValue}, "
        #     f"distance to pacman: {distanceToPacman}, "
        #     f"pellet level: {pelletLevel}"
        # )

        # Danger zone multipliers
        if mapPos.isInDangerZone:
            dangerLevel *= 1 + weights.get('dangerZoneMultiplier')
            if mapPos.dangerZone.vectorIsMidMapNode(vector):
                dangerLevel *= 1 + weights.get('dangerZoneMiddleMapNodeMultiplier')

        # a ghost is closer than pacman multiplier
        if obs.map.calculateDistance(obs.getPacmanPosition(), vector) > minGhostDistance:
            dangerLevel *= 1 + weights.get('ghostIsCloserMultiplier')

        # close to edge multiplier
        if distanceToNearestEdge(vector) < 40:
            dangerLevel *= 1 + weights.get('edgeMultiplier')

        # Normalize based on total distance to avoid high values in less dangerous situations
        normalizedDanger = dangerLevel / (totalGhostDistance + 1)

        return round(normalizedDanger, 5)

    def getDirection(self, obs: Observation, vector: Vector2) -> int:
        """
        Get the direction from pacman to a vector
        :param obs: The current observation
        :param vector: The vector to get the direction to
        :return: The direction to the vector
        """
        pacmanPosition = obs.getPacmanPosition()
        if pacmanPosition.y == vector.y:
            if pacmanPosition.x < vector.x:
                return RIGHT
            else:
                return LEFT
        else:
            if pacmanPosition.y < vector.y:
                return DOWN
            else:
                return UP

    @staticmethod
    def getBestWeightContainer() -> WeightContainer:
        """
        :return: The best known weight container for this agent
        """
        return WeightContainer({
            'fleeThreshold': 0.0053,
            'pelletLevelDistance': 0.86214,
            'tooCloseThreshold': 5.41053,
            'tooCloseValue': 680.17615,
            'tooFarAwayThreshold': 27.61354,
            'dangerZoneMultiplier': 0.0012,
            'dangerZoneMiddleMapNodeMultiplier': 0.01893,
            'ghostIsCloserMultiplier': 0.00016,
            'edgeMultiplier': 0.08522,
            'pelletLevelDistanceInDangerLevel': 3.16686,
            'pelletsInDangerLevelMultiplier': 8.45353,
            'distanceToPacManMultiplier': 0.00736,
            'PelletIslandDistance': 47.47015,
            'IslandSizeMultiplier': 0.00173,
            'IslandDistanceMultiplier': 10176.32694,
            'ghostMultiplier': 0.00286,
            'blinky': 0.08615,
            'pinky': 4e-05,
            'inky': 5.45433,
            'clyde': 9.29069}
        )

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        """
        :return: The default weight container for this agent (used in the genetic algorithm to create start population)
        """
        return WeightContainer({
            'fleeThreshold': 0.5,
            'pelletLevelDistance': 60,
            'tooCloseThreshold': 300,
            'tooCloseValue': 100,
            'tooFarAwayThreshold': 1000,
            'dangerZoneMultiplier': 1,
            'dangerZoneMiddleMapNodeMultiplier': 1,
            'ghostIsCloserMultiplier': 1,
            'edgeMultiplier': 1,

            'pelletLevelDistanceInDangerLevel': 60,
            'pelletsInDangerLevelMultiplier': 1,
            'distanceToPacManMultiplier': 1,

            'PelletIslandDistance': 30,
            'IslandSizeMultiplier': 10,
            'IslandDistanceMultiplier': 100,

            'ghostMultiplier': 10,
            'blinky': 5,
            'pinky': 5,
            'inky': 5,
            'clyde': 5
        })
