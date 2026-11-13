import os
from pathlib import Path

# ==============================================================================
# BASE DIRECTORIES & FILE PATHS
# ==============================================================================
# Points to your project root (one level up from this config/ folder)
BASE_DIR = Path(__file__).resolve().parent.parent

JSON_DIR = BASE_DIR / "jsonFiles"
BACKUP_INDEX_DIR = JSON_DIR / "indexJsonBackups"

INDEX_JSON_PATH = JSON_DIR / "index.json"
NAZAR_JSON_PATH = JSON_DIR / "nazar.json"
EVENTS_JSON_PATH = JSON_DIR / "events.json"

# Output destinations
HTML_OUTPUT_PATH = BASE_DIR / "index.html"
DEBUG_JSON_OUTPUT_PATH = BASE_DIR / "final_challenges_output2.json"

# Front-end asset directories
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Local Nazar images directory (preserves your existing folder)
NAZAR_IMAGES_DIR = BASE_DIR / "HTML" / "images" / "nazar"
NAZAR_PLACEHOLDER_REL = "HTML/images/nazar/RDO_Nazar___Placeholder.png"

# ==============================================================================
# FEATURE FLAGS & RUNTIME CONTROLS
# ==============================================================================
# "auto" (rotate daily) or "force1", "force2", etc.
DESCRIPTION_MODE = "auto"

# Download index.json automatically if expired without terminal prompt
AUTO_DOWNLOAD = True

# Offline testing mode: blocks all external API network requests when True
BLOCK_DOWNLOADS = False

# Appends [Desc #X] tag to descriptions when more than one is available
DEBUG_DESCRIPTION = True

# Daily streak override (-1 = use browser localStorage value)
MANUAL_STREAK = -1

# Print gold tally debug tables to the browser console
ENABLE_JS_DEBUG = True

# Role challenge difficulty filter: "easy", "med", or "hard"
FILTER_DIFFICULTY = "hard"

# Terminal debug logging level: 0 (Off), 1, 2, 3, 4
CURRENT_DEBUG_LEVEL = 1

# ==============================================================================
# API ENDPOINTS & NETWORK SETTINGS
# ==============================================================================
PRIMARY_CHALLENGES_URL = "https://api.rdo.gg/challenges/index.json"
FALLBACK_CHALLENGES_URL = "https://rdo-dailies.com/api/RDO/general/daily_challenges"

PRIMARY_NAZAR_URL = "https://api.rdo.gg/nazar"
FALLBACK_NAZAR_URLS = [
    "https://rdo-dailies.com/api/RDO/collector/madam_nazar",
    "https://rdo-dailies.com/api/RDO/general/madam_nazar",
]

EVENTS_URL = "https://api.rdo.gg/events/"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

# ==============================================================================
# TIME & SCHEDULE CONSTANTS
# ==============================================================================
RDO_RESET_HOUR_UTC = 6           # 06:00 UTC daily reset
EVENTS_WINDOW_HOUR_UTC = 9       # 09:00 UTC weekly reset
EVENTS_COOLDOWN_SHORT = 10800    # 3 hours cooldown for Tue/Wed late checks