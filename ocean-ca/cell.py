# cell.py
import copy
from constants import *

class Cell:
    """
    Represents a single grid cell. It can be either:
      - An environment cell: cell_type in {WATER, SAND, ROCK, CORAL_ROCK, LAVA}
      - An agent (plant) cell: cell_type == AGENT, with additional fields
    """
    __slots__ = (
        "cell_type",     # int: WATER, SAND, etc., or AGENT
        "species_id",    # int or None
        "subtype",       # int: SUBTYPE_UNSPEC, SUBTYPE_ROOT, etc. (only if AGENT)
        "nutrient",      # float: internal nutrient store (agents only)
        "age",           # int: age in steps (agents only)
        "agent_id",      # int: unique ID for each organism (agents only)
        "temp",          # float: temperature (only for LAVA)
        "spore_age"      # int: how long this spore has floated (only if subtype==SPORE)
    )

    def __init__(self, cell_type=WATER, species_id=None, subtype=None):
        self.cell_type = cell_type
        self.species_id = species_id
        self.subtype = subtype
        self.nutrient = 0.0
        self.age = 0
        self.agent_id = None
        self.temp = None
        self.spore_age = 0

    def copy(self):
        """Return a (shallow) copy of this cell."""
        new = Cell()
        new.cell_type = self.cell_type
        new.species_id = self.species_id
        new.subtype = self.subtype
        new.nutrient = self.nutrient
        new.age = self.age
        new.agent_id = self.agent_id
        new.temp = self.temp
        new.spore_age = self.spore_age
        return new

    def is_agent(self):
        return self.cell_type == AGENT

    def is_environment(self):
        return self.cell_type in {WATER, SAND, ROCK, CORAL_ROCK, LAVA}

    def is_rotten(self):
        """
        Return True if an agent cell is dead or about to be replaced by environment.
        (In this code, we check agent death externally, not here.)
        """
        return False

    def __repr__(self):
        if self.cell_type == AGENT:
            return (
                f"<Agent species={self.species_id} subtype={self.subtype} "
                f"age={self.age} nut={self.nutrient:.1f} id={self.agent_id}>"
            )
        else:
            return f"<Env type={self.cell_type} temp={self.temp}>"
