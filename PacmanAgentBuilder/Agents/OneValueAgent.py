from collections import deque

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Qlearning.GameState import GameState
from PacmanAgentBuilder.Utils.Map import MapPosition
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.observation import Observation
from PacmanAgentBuilder.Utils.utils import *
from Pacman_Complete.constants import *
from Pacman_Complete.vector import Vector2


class OneValueAgent(IAgent):
    def __init__(self, gameController, weightContainer: WeightContainer = None):
        super().__init__(gameController, weightContainer=weightContainer)

        self.lastGameStateScore = 0

    def calculateNextMove(self, obs: Observation):
        # factor = GameState.simplifyFactor
        # for x in range(100):
        #     for y in range(100):
        #         if (x*10) % factor == 0 or (y*10) % factor == 0:
        #             DebugHelper.drawDot(Vector2(x*10, y*10), 1, DebugHelper.GREEN)
        #
        # DebugHelper.pauseGame()

        if self.actionsTaken % 5 != 0:
            return STOP

        minMove, minDangerLevel = self.flee(obs, obs.map.createMapPosition(obs.getPacmanPosition()))

        gameStateScore = minDangerLevel

        # gameStateScore = -self.calculateDangerLevel(
        #     obs,
        #     obs.map.createMapPosition(obs.getPacmanPosition()),
        #     obs.getPacmanPosition(),
        #     self.weightContainer
        # )

        print(gameStateScore >= self.lastGameStateScore, gameStateScore - self.lastGameStateScore)
        self.lastGameStateScore = gameStateScore

        return minMove

    def isInDanger(self, obs: Observation, mapPos: MapPosition) -> bool:
        dangerLevel = self.calculateDangerLevel(obs, mapPos, mapPos.mapNode1.position, self.weightContainer)
        if mapPos.isBetweenMapNodes:
            dangerLevel = max(
                dangerLevel,
                self.calculateDangerLevel(obs, mapPos, mapPos.mapNode2.position, self.weightContainer)
            )

        return dangerLevel > self.weightContainer.get('fleeThreshold')

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

    def calculateGameStateScore(self, obs: Observation, mapPos: MapPosition) -> (int, int):
        startMapNode, startIsCustom = obs.map.getOrCreateCustomMapNodeOnVector(obs.getPacmanPosition())

        sumDangerLevel = 0
        for neighborContainer in startMapNode.neighborContainers:
            endMapNode, path, distance = obs.map.getPathToEndOfDangerZoneInDirection(startMapNode,
                                                                                     neighborContainer.direction)

            if obs.isGhostInPath(path):
                # DebugHelper.drawPath(path, DebugHelper.RED, 5)
                continue
            # DebugHelper.drawPath(path, DebugHelper.GREEN, 5)

            dangerLevel = self.calculateDangerLevel(obs, mapPos, endMapNode.position, self.weightContainer)
            # DebugHelper.drawDangerLevel(dangerLevel, endMapNode.position)
            sumDangerLevel += dangerLevel

        return sumDangerLevel

    def flee(self, obs: Observation, mapPos: MapPosition) -> (int, int):
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

        return minDangerDirection, minDangerLevel

    def collect(self, obs: Observation):
        pacmanPosition = obs.getPacmanPosition()

        nextPos = self.calculateTargetPelletPosition(obs)
        # in the rare case that there are no pellets left and the game still asks for a move, return STOP
        if nextPos is None:
            return STOP

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

        if len(closestIslandPositions) == 0:
            return None
        return closestIslandPositions[bestIslandIndex]

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
            'fleeThreshold': 10.3649,
            'pelletLevelDistance': 171.04447,
            'tooCloseThreshold': 0.55431,
            'tooCloseValue': 2.22647,
            'tooFarAwayThreshold': 0.00324,
            'dangerZoneMultiplier': 0.054,
            'dangerZoneMiddleMapNodeMultiplier': 0.00022,
            'ghostIsCloserMultiplier': 0.00322,
            'edgeMultiplier': 1.49241,
            'pelletLevelDistanceInDangerLevel': 619.93584,
            'pelletsInDangerLevelMultiplier': 0.18195,
            'distanceToPacManMultiplier': 0.0,
            'PelletIslandDistance': 0.0,
            'IslandSizeMultiplier': 9.89987,
            'IslandDistanceMultiplier': 1501.86886,
            'ghostMultiplier': 0.00022,
            'blinky': 0.00017,
            'pinky': 0.18026,
            'inky': 1e-05,
            'clyde': 0.0222
        })

    @staticmethod
    def getDefaultWeightContainer() -> WeightContainer:
        """
        :return: The default weight container for this agent (used in the genetic algorithm to create start population)
        """
        return WeightContainer({
            'fleeThreshold': 5,
            'pelletLevelDistance': 100,
            'tooCloseThreshold': 300,
            'tooCloseValue': 100,
            'tooFarAwayThreshold': 1000,
            'dangerZoneMultiplier': 2,
            'dangerZoneMiddleMapNodeMultiplier': 2,
            'ghostIsCloserMultiplier': 2,
            'edgeMultiplier': 2,

            'pelletLevelDistanceInDangerLevel': 60,
            'pelletsInDangerLevelMultiplier': 2,
            'distanceToPacManMultiplier': 2,

            'PelletIslandDistance': 60,
            'IslandSizeMultiplier': 10,
            'IslandDistanceMultiplier': 100,

            'ghostMultiplier': 2,
            'blinky': 2,
            'pinky': 2,
            'inky': 2,
            'clyde': 2
        })
