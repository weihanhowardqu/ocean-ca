# constants.py

# Cell type codes (environment)
WATER = 0
SAND = 1
ROCK = 2
CORAL_ROCK = 3
LAVA = 4

# Agent type code (all plants/spores)
AGENT = 5

# Subtypes for agent cells (for each species)
# We'll use integer codes for subtypes:
#  0 = UNSPECIALIZED (initial state)
#  1 = ROOT/HOLDFAST (attached to substrate)
#  2 = STEM/LEAF (photosynthetic part)
#  3 = REPRODUCTIVE (sporulating/spawning cell)
#  4 = SPORE (free-floating stage)
SUBTYPE_UNSPEC = 0
SUBTYPE_ROOT = 1
SUBTYPE_STEM = 2
SUBTYPE_REPRO = 3
SUBTYPE_SPORE = 4

# Map for pretty names (optional)
CELL_TYPE_NAMES = {
    WATER: "Water",
    SAND: "Sand",
    ROCK: "Rock",
    CORAL_ROCK: "CoralRock",
    LAVA: "Lava",
    AGENT: "Agent",
}

SUBTYPE_NAMES = {
    SUBTYPE_UNSPEC: "Unspec",
    SUBTYPE_ROOT: "Root",
    SUBTYPE_STEM: "Stem/Leaf",
    SUBTYPE_REPRO: "Reproductive",
    SUBTYPE_SPORE: "Spore",
}

# Species IDs
SPECIES_SEAWEED = 0
SPECIES_KELP = 1
SPECIES_SEAGRASS = 2
SPECIES_CORAL = 3

SPECIES_NAMES = {
    SPECIES_SEAWEED: "Seaweed",
    SPECIES_KELP:    "Kelp",
    SPECIES_SEAGRASS: "Seagrass",
    SPECIES_CORAL:   "Coral",
}
