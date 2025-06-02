# species.py
import numpy as np
from constants import *

class MarinePlantSpecies:
    """
    Holds species-specific parameters for each marine 'plant' type.
    """
    def __init__(
        self,
        species_id,
        name,
        allowed_substrates,
        growth_threshold,
        substrate_absorb_rate,
        light_absorb_rate,
        base_repro_prob,
        repro_age,
        max_age,
        spore_life,
        initial_nutrient=5.0
    ):
        self.species_id = species_id
        self.name = name
        self.allowed_substrates = allowed_substrates
        self.growth_threshold = growth_threshold
        self.substrate_absorb_rate = substrate_absorb_rate
        self.light_absorb_rate = light_absorb_rate
        self.base_repro_prob = base_repro_prob
        self.repro_age = repro_age
        self.max_age = max_age
        self.spore_life = spore_life
        self.initial_nutrient = initial_nutrient

    def can_attach(self, below_type):
        """
        Check if this species can attach (root/holdfast) to a given substrate type.
        """
        return below_type in self.allowed_substrates

    def reproduce_chance(self, age):
        """
        Return probability of reproduction given the cell's age.
        """
        if age < self.repro_age:
            return 0.0
        # Could be a function of age; for simplicity use base_proba
        return self.base_repro_prob

    def __repr__(self):
        return f"<Species {self.name}>"

# Create species dictionary
species_defs = {
    SPECIES_SEAWEED: MarinePlantSpecies(
        species_id=SPECIES_SEAWEED,
        name="Seaweed",
        allowed_substrates={ROCK, CORAL_ROCK},
        growth_threshold=10.0,
        substrate_absorb_rate=1.0,
        light_absorb_rate=1.0,
        base_repro_prob=0.02,
        repro_age=8,
        max_age=50,
        spore_life=15,
        initial_nutrient=5.0,
    ),
    SPECIES_KELP: MarinePlantSpecies(
        species_id=SPECIES_KELP,
        name="Kelp",
        allowed_substrates={ROCK},
        growth_threshold=12.0,
        substrate_absorb_rate=1.5,
        light_absorb_rate=1.2,
        base_repro_prob=0.015,
        repro_age=10,
        max_age=60,
        spore_life=20,
        initial_nutrient=6.0,
    ),
    SPECIES_SEAGRASS: MarinePlantSpecies(
        species_id=SPECIES_SEAGRASS,
        name="Seagrass",
        allowed_substrates={SAND},
        growth_threshold=8.0,
        substrate_absorb_rate=1.2,
        light_absorb_rate=0.8,
        base_repro_prob=0.025,
        repro_age=7,
        max_age=45,
        spore_life=12,
        initial_nutrient=4.0,
    ),
    SPECIES_CORAL: MarinePlantSpecies(
        species_id=SPECIES_CORAL,
        name="Coral",
        allowed_substrates={ROCK, CORAL_ROCK},
        growth_threshold=15.0,
        substrate_absorb_rate=1.0,
        light_absorb_rate=1.5,  # relies heavily on light
        base_repro_prob=0.01,
        repro_age=12,
        max_age=80,
        spore_life=25,
        initial_nutrient=7.0,
    ),
}
