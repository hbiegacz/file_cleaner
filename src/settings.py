#!/usr/bin/env python3

import json
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / ".clean_files"

DEFAULTS = {
    "TARGET_PERMISSIONS":         "rw-r--r--",
    "SUSPICIOUS_CHARS":           [" ", "'", '"', ",", ";", "*", "?", "$", "#", "&", "|", "\\"],
    "SUSPICIOUS_CHAR_SUBSTITUTE": "_",
    "TEMP_FILE_PATTERNS":         ["*.tmp", "*~", "*.bak"],
    "DRY_RUN":                    True,
    "KEEP_DUPLICATE_STRATEGY":    "oldest",
    "IGNORED_DIRS":               [".git", "__pycache__", ".DS_Store", "node_modules", ".idea"],
}

_EXPECTED_TYPES = {
    "TARGET_PERMISSIONS":         str,
    "SUSPICIOUS_CHARS":           list,
    "SUSPICIOUS_CHAR_SUBSTITUTE": str,
    "TEMP_FILE_PATTERNS":         list,
    "DRY_RUN":                    bool,
    "KEEP_DUPLICATE_STRATEGY":    str,
    "IGNORED_DIRS":               list,
}

_VALID_DUPLICATE_STRATEGIES = {"oldest", "newest"}

def load_settings() -> dict:
    settings = dict(DEFAULTS)

    if not CONFIG_FILE.exists():
        return settings

    data = _read_config_file()

    for key, value in data.items():
        if key not in DEFAULTS:
            print(f"[settings] Warning: unknown config key '{key}', skipping.")
            continue

        _validate_entry(key, value)
        settings[key] = value

    return settings

def _read_config_file() -> dict:
    try:
        with CONFIG_FILE.open(encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Config file {CONFIG_FILE} is not valid JSON: {e}")
    except OSError as e:
        raise RuntimeError(f"Could not read config file {CONFIG_FILE}: {e}")


def _validate_entry(key: str, value) -> None:
    expected_type = _EXPECTED_TYPES[key]
    if not isinstance(value, expected_type):
        raise ValueError(
            f"Config key '{key}' must be of type {expected_type.__name__}, "
            f"got {type(value).__name__}."
        )

    if key == "KEEP_DUPLICATE_STRATEGY" and value not in _VALID_DUPLICATE_STRATEGIES:
        raise ValueError(
            f"KEEP_DUPLICATE_STRATEGY must be one of {_VALID_DUPLICATE_STRATEGIES}, "
            f"got '{value}'."
        )

def parse_permissions(rwx: str) -> int:
    values = {"r": 4, "w": 2, "x": 1, "-": 0}
    groups = [sum(values[c] for c in rwx[i:i+3]) for i in range(0, 9, 3)]
    return (groups[0] << 6) | (groups[1] << 3) | groups[2]