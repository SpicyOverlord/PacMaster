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

        poolSize = max(int(populationSize * 0.1), 2)

        currentMutationRate = mutationRate

        defaultWeightContainer = agentClass.getDefaultWeightContainer()
        BestWeightContainer = agentClass.getBestWeightContainer()

        # generate random population from the default weight container from the agent
        population = [defaultWeightContainer]
        for i in range(int(populationSize * 0.9)):
            newWeightContainer = WeightModifier.mutateAll(defaultWeightContainer, 1.1)
            population.append(newWeightContainer)
        while len(population) < populationSize:
            newWeightContainer = WeightModifier.mutateAll(BestWeightContainer, 0.7)
            population.append(newWeightContainer)

        # only print start population
        # for pop in population:
        #     print(pop)
        # exit()

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

                start_time = time.time()

                stats = calculatePerformanceOverXGames(
                    agentClass=agentClass,
                    weightContainer=population[i],
                    gameCount=gameCount,
                    lockDeltaTime=True,
                    gameSpeed=15,
                    freightEnabled=True
                )

                end_time = time.time()

                finishedGameCount += gameCount
                print(f"Performance: {stats}")
                population[i].addFitness(stats['combinedScore'])

                # estimate seconds left until simulation is finished
                timeTaken = end_time - start_time
                print(f"Time taken: {secondsToTime(timeTaken)}")

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

        top10population = population[:int(populationSize * 0.1)]
        top10to30population = population[int(populationSize * 0.1):int(populationSize * 0.3)]

        # 10% of the new population will be the top 10% of the previous generation
        newPopulation = top10population
        # 60% of the new population will be a child of the previous generation
        for i in range(int(populationSize * 0.6)):
            parentA = WeightModifier.tournamentSelectParent(population, poolSize)
            parentB = WeightModifier.tournamentSelectParent(population, poolSize)
            child = WeightModifier.blendByFitnessCombine(parentA, parentB)

            # mutate half of the children
            if i % 2 == 0:
                child = WeightModifier.mutateRandom(child, currentMutationRate)

            newPopulation.append(child)

        # 20% of the new population will be a child of the top 10% of the previous generation
        for i in range(int(populationSize * 0.2)):
            parentA = random.choice(top10population)
            parentB = random.choice(top10population)
            child = WeightModifier.blendRandomCombine(parentA, parentB)

            # mutate half of the children
            if i % 2 == 0:
                child = WeightModifier.mutateRandom(child, currentMutationRate)

            newPopulation.append(child)

        # 10% of the new population will be mutations of the top 10% to 30% of the previous generation
        for _ in range(int(populationSize * 0.1)):
            parent = WeightModifier.tournamentSelectParent(top10to30population, 2)
            mutatedParent = WeightModifier.mutateRandom(parent, currentMutationRate)
            newPopulation.append(mutatedParent)

        return newPopulation


DebugHelper.disable()
TournamentRunner.startNewSimulation(FirstRealAgent, 50, 20, 1.5,
                                    50)
