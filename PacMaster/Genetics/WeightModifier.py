import random

from PacMaster.Genetics.WeightContainer import WeightContainer


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

            mutation.addWeight(key, mutatedValue)

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

            mutation.addWeight(key, mutatedValue)

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
    def randomBetweenCombine(weightsA: WeightContainer, weightsB: WeightContainer) -> WeightContainer:
        WeightModifier.checkSameKeySet(weightsA, weightsB)

        # Randomly choose the value from one of the two weights
        offspring = WeightContainer()
        for key, value in weightsA.items():
            offspring.addWeight(key, round(random.uniform(weightsA.getWeight(key), weightsB.getWeight(key)), 3))

        return offspring

    @staticmethod
    def averageCombine(weightsA: WeightContainer, weightsB: WeightContainer) -> WeightContainer:
        WeightModifier.checkSameKeySet(weightsA, weightsB)

        child = WeightContainer()
        for key, value in weightsA.items():
            averageWeight = (value + weightsB.getWeight(key)) / 2
            child.addWeight(key, averageWeight)

        return child

    # TODO: Make a function where alpha is decided by the fitness of the parents?
    @staticmethod
    def blendRandomCombine(weightsA: WeightContainer, weightsB: WeightContainer) -> WeightContainer:
        WeightModifier.checkSameKeySet(weightsA, weightsB)

        offspring = WeightContainer()
        for key, value in weightsA.items():
            # ratio = random.uniform(0.2, 0.8)
            ratio = random.random()
            blendedWeight = (1 - ratio) * value + ratio * weightsB.getWeight(key)
            offspring.addWeight(key, blendedWeight)

        return offspring

    @staticmethod
    def blendByFitnessCombine(weightsA: WeightContainer, weightsB: WeightContainer) -> WeightContainer:
        WeightModifier.checkSameKeySet(weightsA, weightsB)

        if weightsA.getFitness() == 0 and weightsB.getFitness() == 0:
            ratio = 0.5
        else:
            ratio = weightsA.getFitness() / (weightsA.getFitness() + weightsB.getFitness())

        offspring = WeightContainer()
        for key, value in weightsA.items():
            blendedWeight = (1 - ratio) * value + ratio * weightsB.getWeight(key)
            offspring.addWeight(key, blendedWeight)

        return offspring

    @staticmethod
    def tournamentSelectParent(weightsList: list[WeightContainer], poolSize: int) -> WeightContainer:
        tournament = []

        for i in range(poolSize):
            tournament.append(random.choice(weightsList))

        return max(tournament, key=lambda x: x.getFitness())

    @staticmethod
    def rouletteWheelSelectParent(weightsList: list[WeightContainer]) -> WeightContainer:
        totalFitness = sum(weightContainer.getFitness() for weightContainer in weightsList)
        rouletteSpin = random.uniform(0, totalFitness)
        cumulativeFitness = 0

        for weightContainer in weightsList:
            cumulativeFitness += weightContainer.getFitness()
            if cumulativeFitness >= rouletteSpin:
                return weightContainer

    @staticmethod
    def sortByFitness(weightsList: list[WeightContainer]) -> list[WeightContainer]:
        return sorted(weightsList, key=lambda x: x.getFitness(), reverse=True)

    # TODO: remove this when we know everything works!
    @staticmethod
    def checkSameKeySet(weightsA: WeightContainer, weightsB: WeightContainer) -> bool:
        if set(weightsA.keys()) != set(weightsB.keys()):
            raise ValueError("Weights does not have the same keys")

        return True
