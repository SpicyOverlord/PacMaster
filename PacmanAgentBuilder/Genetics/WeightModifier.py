import random

from PacmanAgentBuilder.Genetics.WeightContainer import WeightContainer


class WeightModifier:
    @staticmethod
    def mutateRandom(weights: WeightContainer, mutationRate: float):
        mutation = WeightContainer()

        for key, value in weights.items():
            if random.random() < mutationRate:
                # mutateDistance = random.uniform(0, 1)
                # mutatedValue = value + value * random.uniform(-mutateDistance, mutateDistance) * mutationRate
                mutateDistance = random.uniform(-1, 1) * mutationRate
                mutatedValue = value + value * mutateDistance

                if mutatedValue < 0:
                    mutatedValue *= -1
            else:
                mutatedValue = value

            mutation.addWeight(key, round(mutatedValue, 3))

        return mutation

    @staticmethod
    def mutateAll(weights: WeightContainer, mutationRate):
        mutation = WeightContainer()

        for key, value in weights.items():
            # mutateDistance = random.uniform(random.uniform(0, 1), 1)
            # mutatedValue = value + value * random.uniform(-mutateDistance, mutateDistance) * mutationRate
            mutateDistance = random.uniform(-1, 1)
            mutatedValue = value + value * mutateDistance * mutationRate

            if mutatedValue < 0:
                mutatedValue *= -1

            mutation.addWeight(key, round(mutatedValue, 3))

        return mutation

    @staticmethod
    def randomSelectCombine(weightsA: WeightContainer, weightsB: WeightContainer) -> WeightContainer:
        WeightModifier.checkSameKeySet(weightsA, weightsB)

        # Randomly choose the value from one of the two weights
        offspring = WeightContainer()
        for key, value in weightsA.items():
            if random.random() < 0.5:
                offspring.addWeight(key, value)
            else:
                offspring.addWeight(key, weightsB.getWeight(key))

        return offspring

    @staticmethod
    def tournamentSelectParent(weightsList: list[WeightContainer], poolSize: int) -> WeightContainer:
        tournament = []

        for i in range(poolSize):
            tournament.append(random.choice(weightsList))

        return max(tournament, key=lambda x: x.getFitness())

    # TODO: remove this when we know everything works!
    @staticmethod
    def checkSameKeySet(weightsA: WeightContainer, weightsB: WeightContainer) -> bool:
        if set(weightsA.keys()) != set(weightsB.keys()):
            raise ValueError("Weights does not have the same keys")

        return True

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
