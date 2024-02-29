import random


class WeightContainer:
    def __init__(self, weightDict: dict[str, float] = None):
        self.__weightDict__ = weightDict if weightDict is not None else {}
        self.__fitness__ = -1

    def setFitness(self, fitness: float):
        if self.__fitness__ != -1:
            raise ValueError("Fitness already set")
        self.__fitness__ = fitness

    def getFitness(self) -> float:
        if self.__fitness__ == -1:
            raise ValueError("Fitness not set")
        return self.__fitness__

    def hasFitness(self) -> bool:
        return self.__fitness__ != -1

    def copy(self) -> 'WeightContainer':
        newWeights = WeightContainer()
        for key, value in self.__weightDict__.items():
            newWeights.addWeight(key, value)
        return newWeights

    def addWeight(self, name: str, weight: float):
        if name in self.__weightDict__:
            raise ValueError("Weight with name " + name + " already exists")

        self.__weightDict__[name] = weight

    def getWeight(self, name: str) -> float:
        return self.__weightDict__[name]

    def hasWeight(self, name: str) -> bool:
        return name in self.__weightDict__

    def items(self):
        return self.__weightDict__.items()

    def keys(self):
        return self.__weightDict__.keys()

    def __str__(self):
        return str(self.__weightDict__)
