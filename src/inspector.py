import fnmatch
import stat
from pathlib import Path


def find_duplicates(index: dict[Path, dict]) -> dict[str, list[Path]]:
    hash_map: dict[str, list[Path]] = {}
    for path, meta in index.items():
        file_hash = meta.get("hash")
        if file_hash is None:
            continue
        hash_map.setdefault(file_hash, []).append(path)
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def find_empty_files(index: dict[Path, dict]) -> list[Path]:
    return [path for path, meta in index.items() if meta["size"] == 0]


def find_temporary_files(index: dict[Path, dict], temp_patterns: list[str]) -> list[Path]:
    return [
        path for path in index
        if any(fnmatch.fnmatch(path.name, pattern) for pattern in temp_patterns)
    ]


def find_name_conflicts(index: dict[Path, dict]) -> dict[str, list[Path]]:
    name_map: dict[str, list[Path]] = {}
    for path in index:
        name_map.setdefault(path.name, []).append(path)
    return {name: paths for name, paths in name_map.items() if len(paths) > 1}


def find_bad_permissions(index: dict[Path, dict], target_permissions: int) -> list[Path]:
    return [
        path for path, meta in index.items()
        if meta["permissions"] != target_permissions
    ]


def find_suspicious_names(index: dict[Path, dict], suspicious_chars: list[str]) -> list[Path]:
    char_set = set(suspicious_chars)
    return [path for path in index if _has_suspicious_chars(path.name, char_set)]


def find_missing_files(base: Path, sources: list[Path], index: dict[Path, dict]) -> list[Path]:
    base_names = {path.name for path in index if path.is_relative_to(base)}
    return [
        path for path in index
        if _is_in_sources(path, sources) and path.name not in base_names
    ]


def _has_suspicious_chars(filename: str, char_set: set[str]) -> bool:
    return any(char in filename for char in char_set)


def _is_in_sources(path: Path, sources: list[Path]) -> bool:
    return any(path.is_relative_to(source) for source in sources)