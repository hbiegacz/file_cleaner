''' This file LOADS and manages the CONFIGURATION settings for the program. '''

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

CONFIG_FILE = Path(__file__).parent / ".clean_files"
# CONFIG_FILE = Path(__file__).parent.parent / ".clean_files" # paralell to the src/ directory

DEFAULTS = {
    "TARGET_PERMISSIONS":         "rw-r--r--",
    "SUSPICIOUS_CHARS":           [" ", "'", '"', ",", ";", "*", "?", "$", "#", "&", "|", "\\"],
    "SUSPICIOUS_CHAR_SUBSTITUTE": "_",
    "TEMP_FILE_PATTERNS":         ["*.tmp", "*~", "*.bak"],
    "KEEP_DUPLICATE_STRATEGY":    "oldest",
    "KEEP_SAME_NAME_STRATEGY":    "newest",
    "IGNORED_DIRS": [
        ".git",
        "__pycache__",
        ".DS_Store",
        "node_modules",
        ".idea",
        ".vscode",
        ".venv",
        "venv",
        "env",
        "Python-3.8.10",
    ],
}

_EXPECTED_TYPES = {
    "TARGET_PERMISSIONS":         str,
    "SUSPICIOUS_CHARS":           list,
    "SUSPICIOUS_CHAR_SUBSTITUTE": str,
    "TEMP_FILE_PATTERNS":         list,
    "KEEP_DUPLICATE_STRATEGY":    str,
    "KEEP_SAME_NAME_STRATEGY":    str,
    "IGNORED_DIRS":               list,
}

_VALID_STRATEGIES = {"oldest", "newest"}

def load_settings() -> Dict[str, Any]:
    settings = DEFAULTS.copy()

    if not CONFIG_FILE.exists():
        logger.error(f"[ERROR] Config not found at {CONFIG_FILE}. Using defaults defined in src/settings.py.")
        return settings

    try:
        data = _read_config_file()
        for key, value in data.items():
            if key not in DEFAULTS:
                logger.warning(f"[WARN] Unknown config key '{key}', skipping.")
                continue

            _validate_entry(key, value)
            settings[key] = value
        
        logger.info("Config loaded successfully.")
    except Exception as e:
        logger.error(f"[ERROR] Failed to load config: {e}. Using defaults defined in src/settings.py.")

    return settings

# helpers

def _read_config_file() -> Dict[str, Any]:
    with CONFIG_FILE.open(encoding="utf-8") as f:
        return json.load(f)


def _validate_entry(key: str, value: Any) -> None:
    expected_type = _EXPECTED_TYPES[key]
    if not isinstance(value, expected_type):
        raise TypeError(f"Key '{key}' must be {expected_type.__name__}, got {type(value).__name__}")

    if key in ("KEEP_DUPLICATE_STRATEGY", "KEEP_SAME_NAME_STRATEGY") and value not in _VALID_STRATEGIES:
        raise ValueError(f"'{key}' must be one of {_VALID_STRATEGIES}, got '{value}'")


def parse_permissions(rwx: str) -> int:
    """Converts a string like 'rw-r--r--' to an octal permission integer."""
    mapping = {"r": 4, "w": 2, "x": 1, "-": 0}
    try:
        groups = [sum(mapping[c] for c in rwx[i:i+3]) for i in range(0, 9, 3)]
        return (groups[0] << 6) | (groups[1] << 3) | groups[2]
    except (KeyError, IndexError):
        logger.error(f"[ERROR] Invalid permission string format: '{rwx}'. Expected 9 characters (e.g., 'rw-r--r--').")
        return 0o644