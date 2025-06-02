# environment.py

import random
from constants import *

def update_environment(old_grid, new_grid, width, height):
    """
    Update environment cells (Sand falling, Lava cooling/spreading).
    old_grid: 2D list of Cell (previous state)
    new_grid: 2D list of Cell (copy of old_grid, to be modified)
    """
    # Process sand from bottom up so falling is consistent
    for y in range(height - 2, -1, -1):  # from height-2 down to 0
        for x in range(width):
            cell = old_grid[y][x]
            if cell.cell_type == SAND:
                below = old_grid[y + 1][x]
                # If below is WATER (or air, but we treat only WATER as empty), let sand fall
                if below.cell_type == WATER:
                    # Move sand down
                    new_grid[y][x].cell_type = WATER
                    new_grid[y + 1][x].cell_type = SAND
                    new_grid[y + 1][x].temp = None
                else:
                    # try to slip diagonally if possible (down-left or down-right)
                    moved = False
                    # down-left
                    if x > 0 and old_grid[y + 1][x - 1].cell_type == WATER:
                        new_grid[y][x].cell_type = WATER
                        new_grid[y + 1][x - 1].cell_type = SAND
                        new_grid[y + 1][x - 1].temp = None
                        moved = True
                    # down-right
                    elif x < width - 1 and old_grid[y + 1][x + 1].cell_type == WATER:
                        new_grid[y][x].cell_type = WATER
                        new_grid[y + 1][x + 1].cell_type = SAND
                        new_grid[y + 1][x + 1].temp = None
                        moved = True
                    if not moved:
                        # remain as sand
                        continue

    # Process lava from top down (so newly formed lava doesn't immediately get updated in the same step)
    for y in range(height):
        for x in range(width):
            cell = old_grid[y][x]
            if cell.cell_type == LAVA:
                new_cell = new_grid[y][x]
                # Decrease temperature
                if cell.temp is None:
                    temp = 100  # default initial high temp if not set
                else:
                    temp = cell.temp
                temp -= 5  # cool rate per step
                if temp <= 0:
                    # Solidify into Rock
                    new_grid[y][x].cell_type = ROCK
                    new_grid[y][x].temp = None
                else:
                    new_grid[y][x].temp = temp
                    # Spread to random neighbor water cells
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < width and 0 <= ny < height:
                            if old_grid[ny][nx].cell_type == WATER:
                                # Create new lava cell with slightly lower temp
                                new_grid[ny][nx].cell_type = LAVA
                                new_grid[ny][nx].temp = temp - 10
    # No return; new_grid is modified in place
