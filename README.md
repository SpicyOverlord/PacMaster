# PacmanAgentBuilder

PacmanAgentBuilder enhances the game of Pac-Man from [pacmancode.com](https://pacmancode.com/), providing utilities that facilitate the development of custom Pac-Man agents. It streamlines the agent creation process without including any predetermined algorithms (such as pathfinding), helping developers to implement their own unique strategies from scratch.

## Getting Started

To get started agent building, follow these steps:

1. Fork and clone the repository to your local machine.
2. (Optional) Set up a dedicated Python interpreter for the project on your system.
3. Ensure that the `pygame` and `numpy` libraries are installed. These can be installed using the command `pip install pygame numpy` in your terminal.
4. Begin writing your own agent within the `PacmanAgentBuilder/pacmanAgentBuilder/agents/MyFirstAgent.py` file.
5. Execute the `runner.py` located in the project's root directory to test your agent's performance. Your agent will play 10 games, after which the average score will be printed in your console.

> [!TIP]
> Regularly copy your agent class to maintain a history of your progress, so you can observe your improvements and compare them with previous versions.

## Customizing Game Variables

You can adjust these variables in the `runner.py` file:

- `agentClass`: Specify the agent to be evaluated.
- `gameCount`: Number of games the agent will play.
- `gameSpeed`: Sets the speed of the game from 0.1 (slow) to 5 (fast). Note: For a higher speed, enable `lockDeltaTime`.
- `startLevel`: Choose the starting level for the agent (0 for level one, 1 for level two, and so on).
- `ghostsEnabled`: Toggle ghosts on or off.
- `freightEnabled`: Toggle if the effect of power pellets should be ignored (ghosts turning blue and stops chasing).
- `lockDeltaTime`: When enabled, the game will run at the highest possible speed regardless of the `gameSpeed` setting. This provides a stable test environment as the game speed is bottlenecked by your hardware, and can therefore not go faster than your hardware can handle.
- `logging`: Toggle the logging of game-related information to the console while the agent is playing.

> [!TIP]
> If you want to make the game window larger or smaller, you can change the `WINDOWSIZE` constant (line 1) in the `Pacman_Complete/Constants.py` file.

## Classes and Utilities

### Observation Class

The cornerstone of agent development, this class contains all the necessary information that the agent will need to play the game:

- `getPacmanPosition()`: Returns Pac-Man's current position.
- `getPacmanTarget()`: Returns the position of the node that Pac-Man is currently moving towards.
- `getNodeList()`: Returns a list of all nodes in the current level.
- `getNodeFromVector()`: Returns the node at the provided vector. If no node is found, None is returned.
- `getNodeNeighborList()`: Returns a list of the provided node's neighbors.
- `getPelletPositions()`: Returns a list of all non-eaten pellets' position.
- `getPowerPelletPositions()`: Returns a list of all non-eaten power-pellets' position.
- `getGhostModes()`: Returns a list of all ghosts' modes.
- `getGhostCommonMode()`: Returns the mode that most ghosts are in (CHASE, SCATTER, etc.).
- `getGhosts()`: Returns a list of the ghost objects.
- `getGhostPositions()`: Returns a list of the ghosts' positions.
- `getGhost()`: Returns a ghost object from the provided ghost constant (BLINKY, PINKY, etc.)
- `getBlinky()`: Returns the Blinky object.
- `getPinky()`: Returns the Pinky object.
- `getInky()`: Returns the Inky object.
- `getClyde()`: Returns the Clyde object.

### DebugHelper Class 

The DebugHelper offers static methods that can help with debugging agent behavior and also includes a few colors that can be used in the draw methods:

- `DebugHelper.pauseGame()`: Pauses the game, allowing for step-by-step analysis. Note: to unpause the game, hit the space bar.
- `DebugHelper.disable()`: Disables the DebugHelper.
- `DebugHelper.enable()`: Enables the DebugHelper.
- `DebugHelper.drawLine()`: Draws a line between two vectors.
- `DebugHelper.drawDashedLine()`: Draws a dashed line between two vectors.
- `DebugHelper.drawDot()`: Draws a dot at a vector.
- `DebugHelper.drawDashedCircle()`: Draws a dashed circle around a vector.
- `DebugHelper.drawMap()`: Draws the map/graph of the current level that Pac-Man and the ghosts are moving on.

**The colors are:**
- `DebugHelper.GREEN`
- `DebugHelper.LIGHTBLUE`
- `DebugHelper.YELLOW`
- `DebugHelper.WHITE`
- `DebugHelper.BLUE`
- `DebugHelper.PURPLE`
- `DebugHelper.RED`

### GameStats Class

A GameStats object is returned after an agent has finished a game. It contains information about the game played (the score, levels completed, pellets eaten, and actions taken).

- `GameStats.calculatePerformance()`: This function acts as a performance evaluator over multiple games. It currently calculates the average score of the games.
> [!TIP]
> If you want a more accurate/complex performance function, feel free to edit the `calculatePerformance` method.
