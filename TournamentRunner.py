import random
import time

from PacMaster.Genetics.WeightContainer import WeightContainer
from PacMaster.Genetics.WeightModifier import WeightModifier
from PacMaster.agents.FirstRealAgent import FirstRealAgent
from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.debugHelper import DebugHelper
from PacMaster.utils.runnerFunctions import calculatePerformanceOverXGames
from PacMaster.utils.utils import secondsToTime


class TournamentRunner:
    @staticmethod
    def startNewSimulation(agentClass: type[IAgent], populationSize: int, generationCount: int, mutationRate: float,
                           gameCount: int, gameSpeed: int):
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

        population = [defaultWeightContainer]
        for i in range(populationSize - 1):
            newWeightContainer = WeightModifier.startMutate(defaultWeightContainer)
            population.append(newWeightContainer)

        agentTestingTimes = []
        estimatedSecondsLeft = 0
        for generation in range(generationCount):

            print(f"\n--- Generation {generation + 1} of {generationCount} ---")
            print(f"Mutation rate: {currentMutationRate}")

            for i in range(populationSize):
                # skip if the agent is from the previous generation that already has been tested
                # if population[i].hasFitness():
                #     continue

                print(f"\nRunning agent {i + 1} of {populationSize}...   "
                      f"({round(finishedGameCount / (totalGameCount / 100), 1)}%)   "
                      f"Estimated time left: {secondsToTime(estimatedSecondsLeft)}")
                print(population[i])
                start_time = time.time()  # Record the start time before testing begins

                stats = calculatePerformanceOverXGames(agentClass, population[i],
                                                       gameCount=gameCount, gameSpeed=gameSpeed, freightEnabled=True)
                end_time = time.time()  # Record the end time after testing is finished
                finishedGameCount += gameCount
                print(f"Performance: {stats}")
                population[i].setFitness(stats['combinedScore'])

                # estimate seconds left until simulation is finished
                timeTaken = end_time - start_time
                agentTestingTimes.append(timeTaken)
                averageTimeTaken = sum(agentTestingTimes) / len(agentTestingTimes)
                estimatedSecondsLeft = (totalGameCount - finishedGameCount) / gameCount * averageTimeTaken

                # sort population by fitness
            population = WeightModifier.sortByFitness(population)

            bestOfEachGenerations.append(population[0])

            # print top 5 of previous generation
            # print(f"\nTop 5 of generation {generation + 1}:")
            # for j in range(5):
            #     print(population[j])

            for pop in population:
                print(pop)

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
        newPopulation = []
        for pop in top20population:
            newPopulation.append(pop.copy())
        # 40% of the new population will be offspring of the previous generation
        for _ in range(int(populationSize * 0.2)):
            parentA = WeightModifier.tournamentSelectParent(population, poolSize)
            parentB = WeightModifier.tournamentSelectParent(population, poolSize)
            offspring = WeightModifier.blendByFitnessCombine(parentA, parentB)

            newPopulation.append(offspring)
            newPopulation.append(WeightModifier.mutate(offspring, currentMutationRate))
        # 20% of the new population will be offspring of the top 20% of the previous generation
        for _ in range(int(populationSize * 0.1)):
            parentA = random.choice(top20population)
            parentB = random.choice(top20population)
            offspring = WeightModifier.blendCombine(parentA, parentB)

            newPopulation.append(offspring)
            newPopulation.append(WeightModifier.mutate(offspring, currentMutationRate * 0.5))
        # 20% of the new population will be mutations of the top 20% of the previous generation
        for _ in range(int(populationSize * 0.2)):
            newPopulation.append(WeightModifier.mutate(random.choice(top20population), currentMutationRate))

        return newPopulation


DebugHelper.disable()
TournamentRunner.startNewSimulation(FirstRealAgent, 40, 20, 1.5,
                                    50, 15)
