import random
import time
import multiprocessing
import os

from PacmanAgentBuilder.Agents.FinalAgent import FinalAgent
from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer
from PacmanAgentBuilder.Utils.GameStats import GameStats

from PacmanAgentBuilder.Genetics.WeightModifier import WeightModifier
from PacmanAgentBuilder.Agents.Other.Iagent import IAgent
from PacmanAgentBuilder.Utils.debugHelper import DebugHelper
from PacmanAgentBuilder.Utils.runnerFunctions import calculatePerformanceOverXGames
from PacmanAgentBuilder.Utils.utils import secondsToTime, getCurrentTimestamp

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"


class TournamentRunner:
    """
    This class is used to run a genetic algorithm tournament for a specified agent.
    It is used to find the (hopefully) optimal weights for the agent.
    """

    @staticmethod
    def startNewTournament(agentClass: type[IAgent], populationSize: int, generationCount: int,
                           freeGenerationCount: int, savePercentage: int, mutationRate: float,
                           gameCount: int, cpuCount: int, timeoutSeconds: int):
        """
        This method starts a new genetic algorithm tournament for the specified agent.
        :param agentClass: The specified agent.
        :param populationSize: The size of the population.
        :param generationCount: The number of generations.
        :param freeGenerationCount: The number of generations to skip before save top x% and starting to decrease the mutation rate.
        :param savePercentage: The top percentile of the population to save each generation.
        :param mutationRate: The start mutation rate.
        :param gameCount: The number of games each agent will play each generation to calculate its fitness.
        :param cpuCount: The number of CPU cores to use for parallel fitness evaluation.
        :param timeoutSeconds: The number of seconds to wait for each agent to finish its game before timing out.
        :return: None
        """

        # set some variables that is used in the tournament
        tournamentStartTime = time.time()
        logFileName = f"Tournaments/{getCurrentTimestamp()}_{agentClass.__name__}.txt"
        allMembers = []
        bestOfEachGenerations = []
        totalGameCount = populationSize * generationCount * gameCount
        poolSize = max(int(populationSize * 0.1), 2)  # 10% of the population size, but minimum 2
        constArgs = (agentClass, gameCount)

        # calculate the mutation rate multiplier
        # this is done to decrease the mutation rate each generation so the last generations mutation rate is 0.1
        currentMutationRate = mutationRate
        mutationRateMultiplier = (10 ** (-1 / (generationCount - freeGenerationCount))) * (1 / mutationRate) ** (
                1 / (generationCount - freeGenerationCount))

        # generate start population
        defaultWeightContainer = agentClass.getDefaultWeightContainer()

        prePopulation = [
            WeightContainer(
                {'fleeThreshold': 7.60937, 'pelletLevelDistance': 0.10431, 'tooCloseThreshold': 86.32886,
                 'tooCloseValue': 192355.37865, 'tooFarAwayThreshold': 0.00287, 'dangerZoneMultiplier': 5e-05,
                 'dangerZoneMiddleMapNodeMultiplier': 1.31001, 'ghostIsCloserMultiplier': 0.46973,
                 'edgeMultiplier': 0.17925, 'pelletLevelDistanceInDangerLevel': 212.96985,
                 'pelletsInDangerLevelMultiplier': 0.11793, 'distanceToPacManMultiplier': 0.16287,
                 'PelletIslandDistance': 0.11847, 'IslandSizeMultiplier': 0.00949, 'IslandDistanceMultiplier': 45.60294,
                 'ghostMultiplier': 0.11594, 'blinky': 0.09273, 'pinky': 1142.2821, 'inky': 0.02258, 'clyde': 0.27173}),
            WeightContainer(
                {'fleeThreshold': 7.56977, 'pelletLevelDistance': 0.07855, 'tooCloseThreshold': 223.7031,
                 'tooCloseValue': 360948.88277, 'tooFarAwayThreshold': 0.00077,
                 'dangerZoneMultiplier': 0.0001, 'dangerZoneMiddleMapNodeMultiplier': 1.11383,
                 'ghostIsCloserMultiplier': 0.04785, 'edgeMultiplier': 0.21505,
                 'pelletLevelDistanceInDangerLevel': 178.28374, 'pelletsInDangerLevelMultiplier': 0.11514,
                 'distanceToPacManMultiplier': 0.01946, 'PelletIslandDistance': 0.13236,
                 'IslandSizeMultiplier': 0.00995, 'IslandDistanceMultiplier': 46.83615,
                 'ghostMultiplier': 0.20619, 'blinky': 0.14664, 'pinky': 1590.88478, 'inky': 0.01836,
                 'clyde': 0.26981}),
            WeightContainer(
                {'fleeThreshold': 10.3649, 'pelletLevelDistance': 171.04447, 'tooCloseThreshold': 0.55431,
                 'tooCloseValue': 2.22647, 'tooFarAwayThreshold': 0.00324, 'dangerZoneMultiplier': 0.054,
                 'dangerZoneMiddleMapNodeMultiplier': 0.00022, 'ghostIsCloserMultiplier': 0.00322,
                 'edgeMultiplier': 1.49241, 'pelletLevelDistanceInDangerLevel': 619.93584,
                 'pelletsInDangerLevelMultiplier': 0.18195, 'distanceToPacManMultiplier': 0.0,
                 'PelletIslandDistance': 0.0, 'IslandSizeMultiplier': 9.89987,
                 'IslandDistanceMultiplier': 1501.86886, 'ghostMultiplier': 0.00022, 'blinky': 0.00017,
                 'pinky': 0.18026, 'inky': 1e-05, 'clyde': 0.0222}),
            WeightContainer(
                {'fleeThreshold': 5.44416, 'pelletLevelDistance': 65.626, 'tooCloseThreshold': 227.15288,
                 'tooCloseValue': 2.49974, 'tooFarAwayThreshold': 0.37857, 'dangerZoneMultiplier': 0.1006,
                 'dangerZoneMiddleMapNodeMultiplier': 0.00139, 'ghostIsCloserMultiplier': 0.20954,
                 'edgeMultiplier': 0.18078, 'pelletLevelDistanceInDangerLevel': 142.74317,
                 'pelletsInDangerLevelMultiplier': 1.16608, 'distanceToPacManMultiplier': 0.00031,
                 'PelletIslandDistance': 19.37922, 'IslandSizeMultiplier': 19.36952,
                 'IslandDistanceMultiplier': 209.07605, 'ghostMultiplier': 0.04522, 'blinky': 0.01463,
                 'pinky': 0.09518, 'inky': 2.58483, 'clyde': 0.00542}),
            WeightContainer({
                'fleeThreshold': 10.50887, 'pelletLevelDistance': 258.61358,
                'tooCloseThreshold': 17.88223, 'tooCloseValue': 3694.69894,
                'tooFarAwayThreshold': 0.0233, 'dangerZoneMultiplier': 0.06301,
                'dangerZoneMiddleMapNodeMultiplier': 0.8647,
                'ghostIsCloserMultiplier': 1.09873, 'edgeMultiplier': 0.01347,
                'pelletLevelDistanceInDangerLevel': 3.44943,
                'pelletsInDangerLevelMultiplier': 1.34617,
                'distanceToPacManMultiplier': 8e-05, 'PelletIslandDistance': 0.01153,
                'IslandSizeMultiplier': 123.48025, 'IslandDistanceMultiplier': 4.11255,
                'ghostMultiplier': 4.08185, 'blinky': 0.01855, 'pinky': 0.01967,
                'inky': 1.26083, 'clyde': 1.53354}),
            WeightContainer(
                {'fleeThreshold': 0.00463, 'pelletLevelDistance': 520.37405, 'tooCloseThreshold': 66.61675,
                 'tooCloseValue': 39.60558, 'tooFarAwayThreshold': 1846.65423,
                 'dangerZoneMultiplier': 0.79823, 'dangerZoneMiddleMapNodeMultiplier': 5.6567,
                 'ghostIsCloserMultiplier': 0.63348, 'edgeMultiplier': 0.95136,
                 'pelletLevelDistanceInDangerLevel': 445.49403, 'pelletsInDangerLevelMultiplier': 1.26128,
                 'distanceToPacManMultiplier': 0.91522, 'PelletIslandDistance': 12.71718,
                 'IslandSizeMultiplier': 1.60958, 'IslandDistanceMultiplier': 379.03204,
                 'ghostMultiplier': 1.904, 'blinky': 48.20524, 'pinky': 11.39158, 'inky': 2.53767,
                 'clyde': 44.10417}),
            WeightContainer(
                {'fleeThreshold': 0.20279, 'pelletLevelDistance': 12.96206, 'tooCloseThreshold': 0.0029,
                 'tooCloseValue': 42.43723, 'tooFarAwayThreshold': 1.11535, 'dangerZoneMultiplier': 7e-05,
                 'dangerZoneMiddleMapNodeMultiplier': 0.00025, 'ghostIsCloserMultiplier': 0.09,
                 'edgeMultiplier': 0.1508, 'pelletLevelDistanceInDangerLevel': 231.8367,
                 'pelletsInDangerLevelMultiplier': 1.51862, 'distanceToPacManMultiplier': 0.00017,
                 'PelletIslandDistance': 2.02816, 'IslandSizeMultiplier': 0.00465,
                 'IslandDistanceMultiplier': 0.28114, 'ghostMultiplier': 0.00462, 'blinky': 0.01564,
                 'pinky': 0.00228, 'inky': 0.09382, 'clyde': 0.15579}),
            WeightContainer(
                {'fleeThreshold': 0.64834, 'pelletLevelDistance': 6.80099, 'tooCloseThreshold': 1.65777,
                 'tooCloseValue': 374.82911, 'tooFarAwayThreshold': 0.2217,
                 'dangerZoneMultiplier': 0.00551, 'dangerZoneMiddleMapNodeMultiplier': 0.01326,
                 'ghostIsCloserMultiplier': 0.00387, 'edgeMultiplier': 2.96274,
                 'pelletLevelDistanceInDangerLevel': 1434.80925, 'pelletsInDangerLevelMultiplier': 0.02618,
                 'distanceToPacManMultiplier': 0.10388, 'PelletIslandDistance': 17.12896,
                 'IslandSizeMultiplier': 1.80522, 'IslandDistanceMultiplier': 40.00913,
                 'ghostMultiplier': 1.01938, 'blinky': 0.01684, 'pinky': 0.03808, 'inky': 2.67903,
                 'clyde': 0.34154})
        ]
        population = []
        population += prePopulation
        # each member of the population is a very mutated version of the default weight container
        while len(population) < populationSize:
            newWeightContainer = WeightModifier.mutateRandom(random.choice(prePopulation), 2)
            population.append(newWeightContainer)

        print("\n\n------------- Starting new genetic tournament -------------")
        print(f"Starting at: {getCurrentTimestamp()}")
        print(f"Agent: {agentClass.__name__}")
        print(f"{totalGameCount} games will be played over "
              f"{generationCount} generations with a population size of {populationSize}.")
        print(f"Each agent will be tested on {gameCount} games, using {cpuCount} CPU cores.")

        for generation in range(generationCount):
            print(f"\n\n------------- Generation {generation + 1} of {generationCount} -------------")
            print(f"Started at: {getCurrentTimestamp()}")
            print(f"Mutation rate: {currentMutationRate}")

            # calculate fitness of population
            start_time = time.time()
            stats = TournamentRunner.parallelFitnessEvaluation(population, constArgs, timeoutSeconds, cpuCount)
            end_time = time.time()

            # add the calculated fitness to each member of the population
            for j in range(populationSize):
                # if the agent timed out, set its fitness to 0
                if stats[j] is None:
                    population[j].addFitness(0)
                    continue

                population[j].addFitness(stats[j]['combinedScore'])

            # sort population by fitness (with stats)
            paired_sorted_lists = sorted(zip(population, stats), key=lambda x: x[0].getFitness(), reverse=True)
            population, stats = zip(*paired_sorted_lists)
            population = list(population)
            stats = list(stats)

            # calculate the time taken to calculate the fitness of the generation
            currentRuntime = time.time() - tournamentStartTime
            progress = (generation + 1) / generationCount * 100
            estimatedSecondsLeft = currentRuntime / progress * (100 - progress)
            generationTimeTaken = end_time - start_time

            # print the stats of the generation
            print("\nAgent      Fitness  Avg Lvl Comp  Survived")
            for i in range(populationSize):
                print("{:<10} {:<8} {:<13} {:<8}".format(
                    f"{i + 1} of {populationSize}",
                    population[i].getFitness(),
                    stats[i]['averageLevelsCompleted'],
                    population[i].getGenerationsSurvived()
                ))
            print(f"Generation took:     {secondsToTime(generationTimeTaken)}")
            print(f"Estimated time left: {secondsToTime(estimatedSecondsLeft)}")
            print(f"Current runtime:     {secondsToTime(currentRuntime)}")
            print(f"Progress:            {round(progress, 1)}%")

            # save the best of the generation
            bestOfEachGenerations.append(population[0])
            # print the best of the generation
            print("\nBest of each generations:")
            print("Generation Fitness Survived")
            for j in range(len(bestOfEachGenerations)):
                print("{:<10} {:<7} {:<8}".format(
                    f"Gen {j + 1}",
                    bestOfEachGenerations[j].getFitness(),
                    bestOfEachGenerations[j].getGenerationsSurvived()
                ))

            # write all evaluated members to a log file.
            allMembers += population
            allMembers = list(set(allMembers))
            allMembers.sort(key=lambda x: x.getFitness(), reverse=True)
            with open(logFileName, 'w') as file:
                file.write("{:<8} {:<13} {:<200}\n".format('Fitness', 'Gen Survived', 'Weights'))

                for i in range(len(allMembers)):
                    file.write("{:<8} {:<13} {:<200}\n".format(
                        allMembers[i].getFitness(),
                        allMembers[i].getGenerationsSurvived(),
                        str(allMembers[i])
                    ))

            # generate the new population for the next generation
            newPopulation = WeightModifier.generateNewPopulation(
                population=population,
                populationSize=populationSize,
                savePercentage=savePercentage,
                currentMutationRate=currentMutationRate,
                poolSize=poolSize,
                freeGenerationCount=freeGenerationCount,
                generation=generation
            )
            population = newPopulation

            # decrease mutation rate each generation
            # skip first x generations
            if generation < freeGenerationCount:
                continue
            currentMutationRate *= mutationRateMultiplier

        print(f"\nThe tournament took: {secondsToTime(time.time() - tournamentStartTime)}")
        print(f"The tournament finished at: {getCurrentTimestamp()}")

    @staticmethod
    def parallelFitnessEvaluation(population, constArgs, timeoutSeconds, cpuCount):
        """
        This method is used to evaluate the fitness of the population in parallel.
        :param population: The population to evaluate.
        :param constArgs: The constant arguments to pass to the fitness function (agentClass, gameCount).
        :param timeoutSeconds: The number of seconds to wait for each agent to finish its game before timing out.
        :param cpuCount: The number of CPU cores to use for parallel fitness evaluation.
        :return: A list of the calculated fitness of the population.
        """
        # create a pool of workers
        with multiprocessing.Pool(processes=cpuCount) as pool:
            results = [pool.apply_async(TournamentRunner.fitnessFunctionWrapper, (member, constArgs)) for member in
                       population]
            finished_stats = []

            # get the population's calculated fitness from the pool.
            for i in range(len(results)):
                try:
                    finished_stats.append(results[i].get(timeout=timeoutSeconds))
                except multiprocessing.TimeoutError:
                    print(f"An agent timed out!")
                    finished_stats.append(GameStats.getEmpty())

            return finished_stats

    @staticmethod
    def fitnessFunctionWrapper(member, args):
        """
        This method is used to wrap the fitness function, so it can be used in the multiprocessing pool.
        :param member: The member to evaluate.
        :param args: The constant arguments to pass to the fitness function (agentClass, gameCount).
        :return: The calculated fitness of the member.
        """
        # disable the DebugHelper, so it doesn't low down the fitness evaluation
        DebugHelper.disable()

        # calculate the fitness of the member
        agentClass = args[0]
        gameCount = args[1]
        try:
            stats = calculatePerformanceOverXGames(
                agentClass=agentClass,
                weightContainer=member,
                gameCount=gameCount,
                lockDeltaTime=True
            )
        except Exception as e:
            print(f"An error occurred during fitness evaluation: {e}")
            stats = GameStats.getEmpty()

        return stats


if __name__ == "__main__":
    DebugHelper.disable()

    # start a new tournament
    TournamentRunner.startNewTournament(
        agentClass=FinalAgent,  # Specify the agent to be evaluated.
        populationSize=24,  # The size of the population.
        freeGenerationCount=0,  # generations to skip before save top x% and starting to decrease the mutation rate.
        generationCount=40,  # The number of generations.
        savePercentage=20,  # The top percentile of the population to save each generation.
        mutationRate=1,  # The start mutation rate.
        gameCount=50,  # The number of games each agent will play each generation to calculate its fitness.
        cpuCount=6,  # multiprocessing.cpu_count(),
        timeoutSeconds=30 * 60  # The number of seconds to wait for each agent to finish its game before timing out.
    )
