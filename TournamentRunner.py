import math
import random
import time

from PacMaster.Genetics.WeightContainer import WeightContainer
from PacMaster.Genetics.WeightModifier import WeightModifier
from PacMaster.agents.FirstRealAgent import FirstRealAgent
from PacMaster.agents.HumanAgent import HumanAgent
from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.runnerFunctions import calculatePerformanceOverXGames
from PacMaster.utils.utils import secondsToTime


class TournamentRunner:
    @staticmethod
    def startNewSimulation(agentClass: type[IAgent], populationSize: int, generationCount: int, mutationRate: float,
                           gameCount: int):
        totalGameCount = populationSize * generationCount * gameCount
        finishedGameCount = 0
        print("--- Starting new simulation ---")
        print(f"Agent: {agentClass.__name__}")
        print(f"{totalGameCount} games will be played over "
              f"{generationCount} generations with a population size of {populationSize}.")

        bestOfEachGenerations = []
        averageOfEachGeneration = []

        # poolSize = max(min(int(populationSize * 0.1), 5), 2)
        poolSize = int(populationSize * 0.2)

        currentMutationRate = mutationRate
        mutationRateMultiplier = (10 ** (-1 / generationCount)) * (1 / mutationRate) ** (1 / generationCount)

        defaultWeightContainer = WeightContainer()
        defaultWeightContainer.addWeight('testValue', 10)
        defaultWeightContainer.addWeight('testValue1', 10)
        defaultWeightContainer.addWeight('testValue2', 10)
        defaultWeightContainer.addWeight('testValue3', 10)
        defaultWeightContainer.addWeight('testValue4', 1)
        defaultWeightContainer.addWeight('testValue5', 1)
        defaultWeightContainer.addWeight('testValue6', 10)
        defaultWeightContainer.addWeight('testValue7', 10)
        defaultWeightContainer.addWeight('testValue8', 10)
        defaultWeightContainer.addWeight('testValue9', 10)
        defaultWeightContainer.addWeight('testValue10', 10)
        defaultWeightContainer.addWeight('testValue11', 10)
        defaultWeightContainer.addWeight('testValue12', 10)
        # defaultWeightContainer = agentClass.getDefaultWeightContainer()
        # BestWeightContainer = agentClass.getBestWeightContainer()

        # generate random population from the default weight container from the agent
        population = []
        while len(population) < populationSize:
            newWeightContainer = WeightModifier.mutateAll(defaultWeightContainer, 10)
            population.append(newWeightContainer)

        # only print start population
        # for pop in population:
        #     print(pop)
        # exit()

        agentTestingTimes = []
        estimatedSecondsLeft = 0
        for generation in range(generationCount):

            # print(f"\n--- Generation {generation + 1} of {generationCount} ---")
            # print(f"Mutation rate: {currentMutationRate}")

            for i in range(populationSize):
                # print(f"\nRunning agent {i + 1} of {populationSize}...   "
                #       f"({round(finishedGameCount / (totalGameCount / 100), 1)}%)   "
                #       f"Estimated time left: {secondsToTime(estimatedSecondsLeft)}")
                # print(population[i])

                start_time = time.time()

                # stats = calculatePerformanceOverXGames(
                #     agentClass=agentClass,
                #     weightContainer=population[i],
                #     gameCount=gameCount,
                #     lockDeltaTime=True,
                #     gameSpeed=15,
                #     freightEnabled=True
                # )
                jitter = 0.2

                value = TournamentRunner.valueFunction(population[i]) * random.uniform(1 - jitter, 1 + jitter)

                difference = abs(value - 1000)
                normalized_difference = 1.0 - (difference / 1000.0)
                fitness = max(0.0, min(1.0, normalized_difference))

                stats = {'combinedScore': fitness}

                end_time = time.time()

                finishedGameCount += gameCount
                # print(f"Performance: {stats}")
                population[i].addFitness(stats['combinedScore'])

                # estimate seconds left until simulation is finished
                timeTaken = end_time - start_time
                # print(f"Time taken: {secondsToTime(timeTaken)}")

                agentTestingTimes.append(timeTaken)
                # the average time is only calculated from the last 2 generations of games.
                # this is because as the agents improve, the games will take longer,
                # and therefore the average will be more accurate if it only includes the most recent games.
                if len(agentTestingTimes) > populationSize * 2:
                    agentTestingTimes.pop(0)

                averageTimeTaken = sum(agentTestingTimes) / len(agentTestingTimes)
                estimatedSecondsLeft = (totalGameCount - finishedGameCount) / gameCount * averageTimeTaken

                # sort population by fitness
            population = WeightModifier.sortByFitness(population)

            bestOfEachGenerations.append(population[0])

            averageSum = 0
            for i in range(populationSize):
                averageSum += TournamentRunner.valueFunction(population[i])
            averageSum /= populationSize
            averageOfEachGeneration.append(averageSum)

            # print top 5 of previous generation
            # print(f"\nTop 5 of generation {generation + 1}:")
            # for j in range(min(5, populationSize)):
            #     print(population[j])

            # print all of previous generation
            # for pop in population:
            #     print(pop)

            newPopulation = TournamentRunner.generateNewPopulation(
                population=population,
                populationSize=populationSize,
                currentMutationRate=currentMutationRate,
                poolSize=poolSize
            )
            population = newPopulation

            # decrease mutation rate
            # currentMutationRate -= mutationRate / generationCount
            currentMutationRate *= mutationRateMultiplier

        print("\nBest of each generations:")
        for i in range(len(bestOfEachGenerations)):
            print(f"Generation {i + 1}: {bestOfEachGenerations[i].getFitness()}",
                  TournamentRunner.valueFunction(bestOfEachGenerations[i]),
                  averageOfEachGeneration[i])

    @staticmethod
    def generateNewPopulation(population: list[WeightContainer], populationSize: int,
                              currentMutationRate: float, poolSize: int) -> list[WeightContainer]:
        # 10% of the new population will be the top 10% of the previous generation
        newPopulation = population[:int(populationSize * 0.1)]
        # newPopulation = []
        # 90% of the new population will be a child of the previous generation
        while len(newPopulation) < populationSize:
            parentA = WeightModifier.tournamentSelectParent(population, poolSize)
            parentB = WeightModifier.tournamentSelectParent(population, poolSize)

            child = WeightModifier.randomSelectCombine(parentA, parentB)
            child = WeightModifier.mutateRandom(child, currentMutationRate)

            newPopulation.append(child)

        return newPopulation

    @staticmethod
    def valueFunction(weights: WeightContainer):
        x0 = weights.getWeight('testValue')
        x1 = weights.getWeight('testValue1')
        x2 = weights.getWeight('testValue2')
        x3 = weights.getWeight('testValue3')
        x4 = weights.getWeight('testValue4')
        x5 = weights.getWeight('testValue5')
        x6 = weights.getWeight('testValue6')
        x7 = weights.getWeight('testValue7')
        x8 = weights.getWeight('testValue8')
        x9 = weights.getWeight('testValue9')
        x10 = weights.getWeight('testValue10')
        x11 = weights.getWeight('testValue11')
        x12 = weights.getWeight('testValue12')

        result = math.sin(x0) ** 2 + math.cos(x1) * x2 + math.log(1 + x5 ** 2)
        result += math.sqrt(abs(x6)) * math.tanh(x7 ** 2 - x8) * x9 ** (1 / 3)

        if x10 > 0:
            result += x10 ** 2.7 / math.log(x10 + 2)
        else:
            result -= math.cosh(x10) * math.atan(x11)

        if x11 < 0:
            result += (x11 ** 2 + x12) ** 0.5
        else:
            result -= x12 * math.exp(-x11)

        for i in range(1, 5):
            result += (x4 ** i) / (i + x6) * math.sinh(x5 * i)

        result += sum(math.sin(x0 + i) * math.cos(x1 * i) for i in range(1, 6))

        result *= (1 + math.erf(x2 * x3 - x4 * x5 + x6 * x7 - x8 * x9 + x10 * x11 - x12))

        return result


DebugHelper.disable()
TournamentRunner.startNewSimulation(FirstRealAgent, 20, 40, 1.5, 30)
