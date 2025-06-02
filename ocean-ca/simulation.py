# simulation.py

import random
import numpy as np
from collections import defaultdict
from constants import *
from cell import Cell
from species import species_defs
from environment import update_environment

class Simulation:
    """
    Main simulation class for the ocean CA.
    """
    def __init__(self, width=100, height=100, seed=None):
        self.width = width
        self.height = height
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        # Create a grid of Cell objects
        self.grid = [[Cell(cell_type=WATER) for _ in range(width)] for _ in range(height)]
        self.next_agent_id = 1  # for assigning unique IDs to individual organisms
        # Current: (dx, dy) and strength (0=no current)
        self.current = {'dx': 0, 'dy': 0, 'strength': 0.0}

        # Data logs
        self.time_step = 0
        self.cell_counts = []   # list of dict: species -> cell_count
        self.indiv_counts = []  # list of dict: species -> individual_count

        # Initialize environment: bottom row = ROCK to catch sand, etc.
        for x in range(width):
            self.grid[height - 1][x].cell_type = ROCK

    def plant_seed(self, x, y, species_id):
        """
        Place an initial seed (two cells) of a given species at (x, y) if valid.
        The seed consists of one ROOT cell (attached) and one STEM cell above it.
        """
        spec = species_defs[species_id]
        # Must attach to allowed substrate
        below_type = self.grid[y + 1][x].cell_type if y + 1 < self.height else WATER
        if not spec.can_attach(below_type):
            return False

        # Create the root cell
        cell_root = self.grid[y][x]
        cell_root.cell_type = AGENT
        cell_root.species_id = species_id
        cell_root.subtype = SUBTYPE_ROOT
        cell_root.nutrient = spec.initial_nutrient
        cell_root.age = 0
        cell_root.agent_id = self.next_agent_id

        # Create the stem cell above if there's water
        if y - 1 >= 0 and self.grid[y - 1][x].cell_type == WATER:
            cell_stem = self.grid[y - 1][x]
            cell_stem.cell_type = AGENT
            cell_stem.species_id = species_id
            cell_stem.subtype = SUBTYPE_STEM
            cell_stem.nutrient = spec.initial_nutrient / 2.0
            cell_stem.age = 0
            cell_stem.agent_id = self.next_agent_id

        self.next_agent_id += 1
        return True

    def set_current(self, dx, dy, strength):
        """
        Set a uniform current vector (dx, dy) and strength (0→∞).
        dx, dy should be integers (-1, 0, or 1), strength between 0.0 and 1.0
        """
        self.current['dx'] = dx
        self.current['dy'] = dy
        self.current['strength'] = strength

    def erupt_volcano(self, x, y, intensity=20, radius=5):
        """
        Simulate an underwater volcanic eruption centered at (x, y).
        intensity: number of initial lava cells
        radius: max offset for lava spread
        """
        for _ in range(intensity):
            dx = random.randint(-radius, radius)
            dy = random.randint(-radius, radius)
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                cell = self.grid[ny][nx]
                # Overwrite whatever is there with lava
                cell.cell_type = LAVA
                cell.temp = 100  # initial high temperature
                cell.species_id = None
                cell.subtype = None
                cell.nutrient = 0.0
                cell.age = 0
                cell.agent_id = None

    def paint_area(self, x1, y1, x2, y2, new_type):
        """
        Change cell_type in the rectangular area from (x1,y1) to (x2,y2) inclusive to new_type.
        new_type must be one of {WATER, SAND, ROCK, CORAL_ROCK}.
        """
        x1c, x2c = max(0, min(x1, x2)), min(self.width - 1, max(x1, x2))
        y1c, y2c = max(0, min(y1, y2)), min(self.height - 1, max(y1, y2))
        for y in range(y1c, y2c + 1):
            for x in range(x1c, x2c + 1):
                self.grid[y][x].cell_type = new_type
                self.grid[y][x].species_id = None
                self.grid[y][x].subtype = None
                self.grid[y][x].nutrient = 0.0
                self.grid[y][x].age = 0
                self.grid[y][x].agent_id = None
                self.grid[y][x].temp = None
                self.grid[y][x].spore_age = 0

    def step(self):
        """
        Advance the simulation by one time step:
          1. Update environment (sand falling, lava cooling/spreading)
          2. Update agents (nutrient absorption, growth proposals, reproduction, death)
          3. Apply proposals
          4. Collect data (populations, etc.)
          5. Increment time_step
        """
        old_grid = self.grid
        # Make a deep copy for new state
        new_grid = [[old_grid[y][x].copy() for x in range(self.width)] for y in range(self.height)]

        # 1. Update environment
        update_environment(old_grid, new_grid, self.width, self.height)

        # Containers for growth/repro proposals: list of dicts
        growth_proposals = []
        repro_proposals = []

        # Track which agent_ids survive to update individual counts later
        survivors = defaultdict(set)

        # 2. Update agents: scan old_grid and build proposals
        for y in range(self.height):
            for x in range(self.width):
                cell = old_grid[y][x]
                if not cell.is_agent():
                    continue

                spec = species_defs[cell.species_id]
                c_new = new_grid[y][x]  # cell in new grid

                # 2a. Aging & nutrient absorption
                # Increase age
                c_new.age = cell.age + 1
                # Substrate absorption if root
                if cell.subtype == SUBTYPE_ROOT:
                    # absorb from substrate below
                    by = y + 1
                    if by < self.height:
                        below_cell = old_grid[by][x]
                        if spec.can_attach(below_cell.cell_type):
                            # Give nutrient to cell
                            c_new.nutrient = cell.nutrient + spec.substrate_absorb_rate
                            # Optional: reduce substrate nutrient, but we do not track substrate nutrient in this simple model
                        else:
                            # Root lost substrate; mark for death
                            c_new.cell_type = WATER
                            c_new.species_id = None
                            c_new.subtype = None
                            c_new.nutrient = 0.0
                            c_new.agent_id = None
                            continue
                    else:
                        # no substrate below → die
                        c_new.cell_type = WATER
                        c_new.species_id = None
                        c_new.subtype = None
                        c_new.nutrient = 0.0
                        c_new.agent_id = None
                        continue
                # Light absorption if stem/leaf or coral: 
                if cell.subtype in (SUBTYPE_STEM, SUBTYPE_REPRO) or cell.species_id == SPECIES_CORAL:
                    # Simplified light model: light ∝ max(0, height_of_surface - y)
                    light_amt = max(0, (self.height - 1 - y) * spec.light_absorb_rate * 0.1)
                    c_new.nutrient = c_new.nutrient + light_amt

                # 2b. Check death by age or starvation
                if c_new.age > spec.max_age or c_new.nutrient < 0.0:
                    # Cell dies
                    if c_new.subtype == SUBTYPE_ROOT:
                        # Turn into Sand when rooted cell dies (nutrient returns)
                        new_grid[y][x].cell_type = SAND
                        new_grid[y][x].nutrient = 0.0
                        new_grid[y][x].species_id = None
                        new_grid[y][x].subtype = None
                        new_grid[y][x].agent_id = None
                    else:
                        # Turn into Water
                        new_grid[y][x].cell_type = WATER
                        new_grid[y][x].nutrient = 0.0
                        new_grid[y][x].species_id = None
                        new_grid[y][x].subtype = None
                        new_grid[y][x].agent_id = None
                    continue

                # Record survival
                survivors[cell.species_id].add(cell.agent_id)

                # 2c. Reproduction chance
                repro_p = spec.reproduce_chance(c_new.age)
                if random.random() < repro_p:
                    # Spawn a spore or larva: find a random nearby spot (within radius 3)
                    # Attempt up to 5 times
                    placed = False
                    for _ in range(5):
                        rx = x + random.randint(-3, 3)
                        ry = y + random.randint(-3, 3)
                        if 0 <= rx < self.width and 0 <= ry < self.height:
                            # Only spawn spore in WATER
                            if old_grid[ry][rx].cell_type == WATER and new_grid[ry][rx].cell_type == WATER:
                                # Create spore cell
                                new_grid[ry][rx].cell_type = AGENT
                                new_grid[ry][rx].species_id = cell.species_id
                                new_grid[ry][rx].subtype = SUBTYPE_SPORE
                                new_grid[ry][rx].nutrient = spec.initial_nutrient * 0.5
                                new_grid[ry][rx].age = 0
                                new_grid[ry][rx].agent_id = self.next_agent_id
                                new_grid[ry][rx].spore_age = 0
                                self.next_agent_id += 1
                                placed = True
                                break
                    # Regardless of success, parent loses some nutrient
                    c_new.nutrient -= spec.growth_threshold * 0.5

                # 2d. Growth: if enough nutrient, try to create a new cell adjacent
                if c_new.nutrient >= spec.growth_threshold:
                    # Prefer upward growth if water above
                    dirs = [(0, -1), (-1, 0), (1, 0), (0, 1)]
                    random.shuffle(dirs)
                    for dx, dy in dirs:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if old_grid[ny][nx].cell_type == WATER and new_grid[ny][nx].cell_type == WATER:
                                # Create a new agent cell
                                new_grid[ny][nx].cell_type = AGENT
                                new_grid[ny][nx].species_id = cell.species_id
                                # Decide subtype based on position: if below substrate, root; else stem
                                below_ty = old_grid[ny + 1][nx].cell_type if ny + 1 < self.height else WATER
                                if spec.can_attach(below_ty):
                                    new_grid[ny][nx].subtype = SUBTYPE_ROOT
                                else:
                                    new_grid[ny][nx].subtype = SUBTYPE_STEM
                                new_grid[ny][nx].nutrient = spec.initial_nutrient * 0.5
                                new_grid[ny][nx].age = 0
                                new_grid[ny][nx].agent_id = cell.agent_id
                                # Deduct nutrient cost
                                c_new.nutrient -= spec.growth_threshold * 0.7
                                break

                # 2e. If this is a spore, attempt attachment or drift
                if cell.subtype == SUBTYPE_SPORE:
                    # First, check if below is suitable substrate
                    by = y + 1
                    if by < self.height:
                        below_type = old_grid[by][x].cell_type
                        if spec.can_attach(below_type):
                            # Attach and become a root
                            new_grid[y][x].subtype = SUBTYPE_ROOT
                            # Give a small bonus nutrient on attachment
                            new_grid[y][x].nutrient += spec.initial_nutrient
                        else:
                            # Not attached; try drifting by current
                            if self.current['strength'] > 0:
                                dx = self.current['dx']
                                dy = self.current['dy']
                                strength = self.current['strength']
                                if random.random() < strength:
                                    tx, ty = x + dx, y + dy
                                    if 0 <= tx < self.width and 0 <= ty < self.height:
                                        if old_grid[ty][tx].cell_type == WATER and new_grid[ty][tx].cell_type == WATER:
                                            # Move spore
                                            new_grid[y][x].cell_type = WATER
                                            new_grid[y][x].species_id = None
                                            new_grid[y][x].subtype = None
                                            new_grid[y][x].nutrient = 0.0
                                            new_grid[y][x].agent_id = None
                                            new_grid[y][x].spore_age = 0
                                            new_spore = new_grid[ty][tx]
                                            new_spore.cell_type = AGENT
                                            new_spore.species_id = cell.species_id
                                            new_spore.subtype = SUBTYPE_SPORE
                                            new_spore.nutrient = cell.nutrient
                                            new_spore.age = cell.age + 1
                                            new_spore.agent_id = cell.agent_id
                                            new_spore.spore_age = cell.spore_age + 1
                                            break
                    # Increment spore_age
                    new_grid[y][x].spore_age = cell.spore_age + 1
                    if new_grid[y][x].spore_age > spec.spore_life:
                        # Spore dies
                        new_grid[y][x].cell_type = WATER
                        new_grid[y][x].species_id = None
                        new_grid[y][x].subtype = None
                        new_grid[y][x].nutrient = 0.0
                        new_grid[y][x].agent_id = None
                        new_grid[y][x].spore_age = 0

        # 3. Swap in new_grid
        self.grid = new_grid

        # 4. Collect data (populations)
        pop_cells = {sid: 0 for sid in SPECIES_NAMES.keys()}
        pop_inds = {sid: set() for sid in SPECIES_NAMES.keys()}
        for y in range(self.height):
            for x in range(self.width):
                c = self.grid[y][x]
                if c.is_agent():
                    pop_cells[c.species_id] += 1
                    pop_inds[c.species_id].add(c.agent_id)
        pop_inds_count = {sid: len(pop_inds[sid]) for sid in pop_inds}

        self.cell_counts.append(pop_cells)
        self.indiv_counts.append(pop_inds_count)

        # 5. Increment time_step
        self.time_step += 1

    def get_latest_counts(self):
        """Return the last recorded cell_counts and indiv_counts."""
        if not self.cell_counts:
            return None, None
        return self.cell_counts[-1], self.indiv_counts[-1]
