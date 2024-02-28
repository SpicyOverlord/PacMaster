import random

from PacMaster.Genetic.WeightContainer import WeightContainer


class Combiner:
    @staticmethod
    def mutate(weights: WeightContainer, mutationRate: float):
        mutation = WeightContainer()

        for key, value in weights.items():
            mutation.addWeight(key, value * random.uniform(-1, 1) * mutationRate)

        return mutation

    @staticmethod
    def randomSelectCombine(weightsA: WeightContainer, weightsB: WeightContainer) -> WeightContainer:
        Combiner.checkSameKeySet(weightsA, weightsB)

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
        Combiner.checkSameKeySet(weightsA, weightsB)

        # Randomly choose the value from one of the two weights
        offspring = WeightContainer()
        for key, value in weightsA.items():
            offspring.addWeight(key, random.uniform(weightsA.getWeight(key), weightsB.getWeight(key)))

        return offspring

    @staticmethod
    def averageCombine(weightsA: WeightContainer, weightsB: WeightContainer) -> WeightContainer:
        Combiner.checkSameKeySet(weightsA, weightsB)

        offspring = WeightContainer()
        for key, value in weightsA.items():
            averageWeight = (value + weightsB.getWeight(key)) / 2
            offspring.addWeight(key, averageWeight)

    # TODO: Make a function where alpha is decided by the fitness of the parents?
    @staticmethod
    def blendCombine(weightsA: WeightContainer, weightsB: WeightContainer) -> WeightContainer:
        Combiner.checkSameKeySet(weightsA, weightsB)

        offspring = WeightContainer()
        for key, value in weightsA.items():
            alpha = random.uniform(0.2, 0.8)
            blendedWeight = (1 - alpha) * value + alpha * weightsB.getWeight(key)
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
    def sortWeights(weightsList: list[WeightContainer]) -> list[WeightContainer]:
        return sorted(weightsList, key=lambda x: x.getFitness(), reverse=True)

    # TODO: remove this when we know everything works!
    @staticmethod
    def checkSameKeySet(weightsA: WeightContainer, weightsB: WeightContainer) -> bool:
        if set(weightsA.keys()) != set(weightsB.keys()):
            raise ValueError("Weights does not have the same keys")

        return True
