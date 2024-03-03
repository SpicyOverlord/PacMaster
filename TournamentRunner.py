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

        poolSize = max(int(populationSize * 0.2), 2)

        currentMutationRate = mutationRate

        defaultWeightContainer = agentClass.getDefaultWeightContainer()

        # generate random population from the default weight container from the agent
        population = [defaultWeightContainer]
        for i in range(int(populationSize*0.7 - 1)):
            newWeightContainer = WeightModifier.startMutate(defaultWeightContainer)
            population.append(newWeightContainer)
        while len(population) < populationSize:
            newWeightContainer = WeightModifier.mutate(defaultWeightContainer, 0.5)
            population.append(newWeightContainer)

        agentTestingTimes = []
        estimatedSecondsLeft = 0
        for generation in range(generationCount):

            print(f"\n--- Generation {generation + 1} of {generationCount} ---")
            print(f"Mutation rate: {currentMutationRate}")

            for i in range(populationSize):
                print(f"\nRunning agent {i + 1} of {populationSize}...   "
                      f"({round(finishedGameCount / (totalGameCount / 100), 1)}%)   "
                      f"Estimated time left: {secondsToTime(estimatedSecondsLeft)}")
                print(population[i])
                start_time = time.time()  # Record the start time before testing begins

                stats = calculatePerformanceOverXGames(agentClass, population[i],
                                                       gameCount=gameCount, lockDeltaTime=True, gameSpeed=15,
                                                       freightEnabled=True)
                end_time = time.time()  # Record the end time after testing is finished
                finishedGameCount += gameCount
                print(f"Performance: {stats}")
                population[i].addFitness(stats['combinedScore'])

                # estimate seconds left until simulation is finished
                timeTaken = end_time - start_time
                agentTestingTimes.append(timeTaken)
                averageTimeTaken = sum(agentTestingTimes) / len(agentTestingTimes)
                estimatedSecondsLeft = (totalGameCount - finishedGameCount) / gameCount * averageTimeTaken

                # sort population by fitness
            population = WeightModifier.sortByFitness(population)

            bestOfEachGenerations.append(population[0])

            # print top 5 of previous generation
            print(f"\nTop 5 of generation {generation + 1}:")
            for j in range(min(5, populationSize)):
                print(population[j])

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
            currentMutationRate *= 0.9

        print("\nBest of each generations:")
        for i in range(len(bestOfEachGenerations)):
            print(f"Generation {i + 1}: {bestOfEachGenerations[i]}")

    @staticmethod
    def generateNewPopulation(population: list[WeightContainer],
                              populationSize: int, currentMutationRate: float, poolSize: int) -> list[WeightContainer]:
        # save some of population
        top20population = population[:int(populationSize * 0.2)]

        # 20% of the new population will be the top 20% of the previous generation
        newPopulation = top20population
        # 40% of the new population will be child of the previous generation
        for _ in range(int(populationSize * 0.2)):
            parentA = WeightModifier.tournamentSelectParent(population, poolSize)
            parentB = WeightModifier.tournamentSelectParent(population, poolSize)
            child = WeightModifier.blendByFitnessCombine(parentA, parentB)

            newPopulation.append(child)
            newPopulation.append(WeightModifier.mutate(child, currentMutationRate))
        # 20% of the new population will be child of the top 20% of the previous generation
        for _ in range(int(populationSize * 0.1)):
            parentA = random.choice(top20population)
            parentB = random.choice(top20population)
            child = WeightModifier.blendCombine(parentA, parentB)

            newPopulation.append(child)
            newPopulation.append(WeightModifier.mutate(child, currentMutationRate * 0.5))
        # 20% of the new population will be mutations of the top 20% of the previous generation
        for _ in range(int(populationSize * 0.2)):
            newPopulation.append(WeightModifier.mutate(random.choice(top20population), currentMutationRate))

        return newPopulation


DebugHelper.disable()
TournamentRunner.startNewSimulation(FirstRealAgent, 50, 20, 1.5,
                                    50)
