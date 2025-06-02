# visualize.py

import matplotlib.pyplot as plt
import numpy as np
from constants import *

def grid_to_color(grid):
    """
    Convert the grid (2D list of Cell) into an RGB image for plotting.
    Returns a (H, W, 3) array of floats in [0,1].
    """
    height = len(grid)
    width = len(grid[0])
    img = np.zeros((height, width, 3), dtype=float)

    # Define colors for environment types
    env_colors = {
        WATER:      (0.0, 0.0, 0.5),    # dark blue
        SAND:       (0.8, 0.7, 0.5),    # tan
        ROCK:       (0.5, 0.5, 0.5),    # gray
        CORAL_ROCK: (0.8, 0.5, 0.5),    # pinkish
        LAVA:       (1.0, 0.2, 0.2),    # red
    }
    # Colors for species (by species_id)
    species_colors = {
        SPECIES_SEAWEED:  (0.0, 0.8, 0.0),   # bright green
        SPECIES_KELP:     (0.0, 0.5, 0.0),   # dark green
        SPECIES_SEAGRASS: (0.5, 1.0, 0.5),   # light green
        SPECIES_CORAL:    (1.0, 0.5, 0.0),   # orange
    }
    for y in range(height):
        for x in range(width):
            c = grid[y][x]
            if c.is_environment():
                img[y, x, :] = env_colors.get(c.cell_type, (1.0, 1.0, 1.0))
            else:
                # Agent cell: color by species, darker if root, lighter if spore
                base = species_colors.get(c.species_id, (1.0, 1.0, 1.0))
                if c.subtype == SUBTYPE_ROOT:
                    factor = 0.6
                elif c.subtype == SUBTYPE_STEM:
                    factor = 1.0
                elif c.subtype == SUBTYPE_REPRO:
                    factor = 0.9
                elif c.subtype == SUBTYPE_SPORE:
                    factor = 0.4
                else:
                    factor = 1.0
                img[y, x, :] = tuple(factor * np.array(base))
    return img

def animate_simulation(sim, steps=200, interval=100):
    """
    Run the simulation for 'steps' steps, showing an animation in Matplotlib.
    'interval' is milliseconds between frames.
    """
    from matplotlib import animation

    fig, ax = plt.subplots(figsize=(6, 6))
    img = ax.imshow(grid_to_color(sim.grid), origin='upper')
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Ocean CA Simulation")

    def update(frame):
        sim.step()
        im = grid_to_color(sim.grid)
        img.set_data(im)
        ax.set_title(f"Step {sim.time_step}")
        return [img]

    ani = animation.FuncAnimation(fig, update, frames=steps, interval=interval, blit=True)
    plt.show()
    return ani
