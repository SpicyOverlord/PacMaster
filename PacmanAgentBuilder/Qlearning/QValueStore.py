import json
import os
import pickle
import time
from typing import List

UNKNOWN_POSITION = -12.3456789


class QValueStore:
    basePath = "QLearningData/"

    def __init__(self):
        self.store = {}

        self.gamma = 0.75  # discount factor
        self.alpha = 0.7  # learning rate
        # self.rho = 0.2  # exploration rate
        self.rho = 0

    def size(self):
        return len(self.store)

    def decayValues(self, decayRate: float) -> None:
        self.alpha *= decayRate
        self.rho *= decayRate

    def getQValues(self, stateHash: int) -> List[float]:
        return self.store.setdefault(stateHash, [UNKNOWN_POSITION, UNKNOWN_POSITION, UNKNOWN_POSITION, UNKNOWN_POSITION])

    def getQValue(self, stateHash: int, madeMove: int) -> float:
        return self.getQValues(stateHash)[madeMove]

    def getMaxQValue(self, stateHash: int) -> float:
        return max(self.getQValues(stateHash))

    def setQValue(self, stateHash: int, actionIndex: int, reward: float) -> None:
        if stateHash not in self.store:
            self.store[stateHash] = [UNKNOWN_POSITION, UNKNOWN_POSITION, UNKNOWN_POSITION, UNKNOWN_POSITION]
        self.store[stateHash][actionIndex] = reward

    def updateQValue(self, lastStateHash: int, lastActionIndex: int, newStateHash: int, reward: float) -> float:
        lastQValue = self.getQValue(lastStateHash, lastActionIndex)
        newStateMaxQValue = self.getMaxQValue(newStateHash)

        newReward = (1 - self.alpha + 0.05) * lastQValue + self.alpha * (reward + self.gamma * newStateMaxQValue)
        # newReward = (1 - self.alpha) * lastQValue + self.alpha * (reward + self.gamma * newStateMaxQValue)

        self.setQValue(lastStateHash, lastActionIndex, newReward)

        return newReward

    def getBestMove(self, stateHash: int) -> (int, float):
        qValues = self.getQValues(stateHash)
        maxQValue = max(qValues)
        return qValues.index(maxQValue), maxQValue

    def saveQValuesToJSON(self, filePath: str, fullPath: bool = False, verbose: bool = True) -> None:
        if fullPath:
            fullPath = filePath
        else:
            fullPath = self.addBasePath(filePath)

        if not os.path.exists(os.path.dirname(fullPath)):
            os.makedirs(os.path.dirname(fullPath))

        if verbose:
            print(f"Saving json to: '{fullPath}' ...", end="")

        start_time = time.time()
        with open(fullPath, 'w') as file:
            json.dump(self.store, file)
        end_time = time.time()

        time_taken = end_time - start_time
        if verbose:
            print(f" Done! ({round(time_taken, 2)} seconds)")

    def loadQValuesFromJSON(self, filePath: str, fullPath: bool = False, verbose: bool = True) -> None:
        if fullPath:
            fullPath = filePath
        else:
            fullPath = self.addBasePath(filePath)

        if verbose:
            print(f"Loading json from: '{fullPath}' ...", end="")
        start_time = time.time()
        try:
            with open(fullPath, 'r') as file:
                self.store = json.load(file)
        except FileNotFoundError:
            print(f"No existing JSON file found at {fullPath}. Starting with an empty Q-value store.")
        end_time = time.time()
        if verbose:
            print(f" Done! ({round(end_time - start_time, 2)} seconds)")

    def saveQValuesToBinary(self, filePath: str, fullPath: bool = False, verbose: bool = True) -> None:
        if fullPath:
            fullPath = filePath
        else:
            fullPath = self.addBasePath(filePath)

        if not os.path.exists(os.path.dirname(fullPath)):
            os.makedirs(os.path.dirname(fullPath))

        if verbose:
            print(f"Saving bin to: '{fullPath}' ...", end="")

        start_time = time.time()
        with open(fullPath, 'wb') as file:
            pickle.dump(self.store, file, protocol=pickle.HIGHEST_PROTOCOL)
        end_time = time.time()

        time_taken = end_time - start_time
        if verbose:
            print(f" Done! ({round(time_taken, 2)} seconds)")

    def loadQValuesFromBinary(self, filePath: str, fullPath: bool = False, verbose: bool = True) -> None:
        if fullPath:
            fullPath = filePath
        else:
            fullPath = self.addBasePath(filePath)

        if verbose:
            print(f"Loading bin from: '{fullPath}' ...", end="")
        start_time = time.time()
        try:
            with open(fullPath, 'rb') as file:
                self.store = pickle.load(file)
        except FileNotFoundError:
            print(f"No existing binary file found at {fullPath}. Starting with an empty Q-value store.")
        end_time = time.time()
        if verbose:
            print(f" Done! ({round(end_time - start_time, 2)} seconds)")

    # def saveQValuesToCompressedBinary(self, filePath: str, chunk_size: int = 10000) -> None:
    #     fullPath = self.addBasePath(filePath)
    #
    #     if not os.path.exists(os.path.dirname(fullPath)):
    #         os.makedirs(os.path.dirname(fullPath))
    #
    #     print(f"Saving compressed bin to: {fullPath}")
    #
    #     # Split the data into chunks
    #     items = list(self.store.items())
    #     chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
    #
    #     # Write each chunk to the file separately
    #     with gzip.open(fullPath, 'wb') as file:
    #         for chunk in chunks:
    #             pickle.dump(dict(chunk), file)
    #
    # def loadQValuesFromCompressedBinary(self, filePath: str) -> None:
    #     fullPath = self.addBasePath(filePath)
    #
    #     try:
    #         with gzip.open(fullPath, 'rb') as file:
    #             while True:
    #                 try:
    #                     chunk = pickle.load(file)
    #                     self.store.update(chunk)
    #                 except EOFError:
    #                     break
    #     except FileNotFoundError:
    #         print(f"No existing compressed binary file found at {fullPath}. Starting with an empty Q-value store.")

    def addBasePath(self, path: str) -> str:
        return self.basePath + path
