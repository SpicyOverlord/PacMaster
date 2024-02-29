from PacMaster.Genetic.WeightModifier import WeightModifier
from PacMaster.agents.FirstRealAgent import FirstRealAgent
from PacMaster.agents.Iagent import IAgent
from PacMaster.utils.runnerFunctions import calculatePerformanceOverXGames


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

        poolSize = int(populationSize * 0.1)
        if poolSize < 2:
            poolSize = 2

        currentMutateRate = mutationRate

        defaultWeightContainer = agentClass.getDefaultWeightContainer()

        population = [defaultWeightContainer]
        for i in range(populationSize-1):
            newWeightContainer = WeightModifier.mutate(defaultWeightContainer, mutationRate)
            population.append(newWeightContainer)

        for generation in range(generationCount):
            currentMutateRate -= mutationRate / generationCount

            print(f"\n--- Generation {generation + 1} of {generationCount} ---")
            for i in range(populationSize):
                # skip if the agent is from the top 20% of the previous generation
                if population[i].hasFitness():
                    continue

                print(f"\nRunning agent {i + 1} of {populationSize}...   ({round(finishedGameCount/(totalGameCount/100),1)}%)")
                print(population[i])
                stats = calculatePerformanceOverXGames(agentClass, population[i],
                                                       gameCount=gameCount, gameSpeed=gameSpeed)
                finishedGameCount += gameCount
                print(f"Performance: {stats}")
                population[i].setFitness(stats['combinedScore'])

            # sort population by fitness
            population = WeightModifier.sortByFitness(population)
            print(f"\nBest of generation {generation+1}:", population[0].getFitness(), population[0])

            # save top 20% of population
            top20population = population[:int(populationSize * 0.2)]
            # create new population
            newPopulation = top20population
            for i in range(int(populationSize * 0.4)):
                parentA = WeightModifier.tournamentSelectParent(population, poolSize)
                parentB = WeightModifier.tournamentSelectParent(population, poolSize)
                offspring = WeightModifier.blendCombine(parentA, parentB)

                newPopulation.append(offspring)
                newPopulation.append(WeightModifier.mutate(offspring, currentMutateRate))

            for pop in population:
                print(pop.getFitness(), pop)
            population = newPopulation


TournamentRunner.startNewSimulation(FirstRealAgent, 50, 10, 1.5,
                                    5, 15)
