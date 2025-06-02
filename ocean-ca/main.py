# main.py

import argparse
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from simulation import Simulation
from visualize import grid_to_color
from constants import (
    SPECIES_SEAWEED,
    SPECIES_KELP,
    SPECIES_SEAGRASS,
    SPECIES_CORAL,
    SAND,
    ROCK,
)

def main():
    parser = argparse.ArgumentParser(description="Run Ocean CA Simulation")
    parser.add_argument("--width", type=int, default=100, help="Grid width")
    parser.add_argument("--height", type=int, default=100, help="Grid height")
    parser.add_argument("--steps", type=int, default=500, help="Number of simulation steps")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    parser.add_argument(
        "--interval",
        type=int,
        default=300,  # increased from 100 → 300 ms between frames (slower)
        help="Milliseconds between animation frames (larger = slower)",
    )
    args = parser.parse_args()

    # 1) Initialize simulation
    sim = Simulation(width=args.width, height=args.height, seed=args.seed)

    # 2) Plant a few seeds of each species near the bottom
    mid_x = args.width // 2
    bottom_y = args.height - 2
    sim.plant_seed(mid_x - 5, bottom_y, SPECIES_SEAWEED)
    sim.plant_seed(mid_x + 5, bottom_y, SPECIES_KELP)
    sim.plant_seed(mid_x - 10, bottom_y, SPECIES_SEAGRASS)
    sim.plant_seed(mid_x + 10, bottom_y, SPECIES_CORAL)

    # 3) Paint substrate patches (sand on left, rock on right)
    sim.paint_area(0, args.height - 5, args.width // 3, args.height - 1, SAND)
    sim.paint_area(args.width // 2, args.height - 5, args.width - 1, args.height - 1, ROCK)

    # 4) Set an initial gentle current to the right
    sim.set_current(dx=1, dy=0, strength=0.2)

    # 5) Schedule a volcanic eruption at step 100 (for demonstration)
    eruption_schedule = {100: (mid_x, args.height - 5, 30, 5)}

    # --- Set up Matplotlib figure and initial image ---
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Ocean CA Simulation (Step 0)")

    # Display the very first frame
    initial_img = grid_to_color(sim.grid)
    img_handle = ax.imshow(initial_img, origin="upper")

    # --- Update function for FuncAnimation ---
    def update(frame):
        # 1) Possibly trigger a volcano this frame
        if sim.time_step in eruption_schedule:
            x, y, intensity, radius = eruption_schedule[sim.time_step]
            sim.erupt_volcano(x, y, intensity=intensity, radius=radius)
            print(f"** Volcano erupted at step {sim.time_step} at ({x},{y}) **")

        # 2) Advance the simulation by one step
        sim.step()

        # 3) Repaint the grid
        new_img = grid_to_color(sim.grid)
        img_handle.set_data(new_img)
        ax.set_title(f"Ocean CA Simulation (Step {sim.time_step})")
        return [img_handle]

    # --- Create and run the animation ---
    anim = FuncAnimation(
        fig,
        update,
        frames=args.steps,      # number of frames = number of steps
        interval=args.interval, # milliseconds between frames
        blit=True,
    )

    plt.tight_layout()
    plt.show()

    # To save at this slower speed, uncomment and adjust fps as needed:
    # anim.save("ocean_ca_slower.mp4", fps=1000/args.interval, dpi=200)
    # anim.save("ocean_ca_slower.gif", writer="imagemagick", fps=1000/args.interval)

if __name__ == "__main__":
    main()
