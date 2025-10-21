from pathlib import Path

# =======================
# Project Settings
# =======================

PROJECT_NAME = "F1 Stats Dashboard"
DATA_SOURCE = "api"
JOLPICA_API_URL = "https://api.jolpi.ca/ergast/f1"
CURRENT_SEASON = 2025
DEFAULT_ENCODING = "utf-8"
LOG_LEVEL = "INFO"

# =======================
# Paths
# =======================

PROJECT_ROOT = Path(__file__).parent.parent  
ASSETS_DIR = PROJECT_ROOT / "assets"
DRIVER_IMAGES_DIR = ASSETS_DIR / "drivers"
CONSTRUCTOR_IMAGES_DIR = ASSETS_DIR / "constructors"
FLAGS_IMAGES_DIR = ASSETS_DIR / "flags"
CURCUITS_IMAGES_DIR = ASSETS_DIR / "circuits"