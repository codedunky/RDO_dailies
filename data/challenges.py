import sys
from pathlib import Path

# Ensure root directory is importable so we can load your existing RDO_challenges_data.py
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import everything directly from your existing data file
from RDO_challenges_data import (
    category_order,
    predefined_challenges,
    trader,
    collector,
    bounty_hunter,
    moonshiner,
    naturalist,
)

# Combined catalog for lookup
all_challenge_definitions = (
    predefined_challenges
    + trader
    + bounty_hunter
    + collector
    + naturalist
    + moonshiner
)