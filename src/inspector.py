import fnmatch
import stat
from pathlib import Path
from typing import List, Dict, Set


def find_duplicates(index: Dict[Path, dict]) -> Dict[str, List[Path]]:
    hash_map: Dict[str, List[Path]] = {}
    for path, meta in index.items():
        file_hash = meta.get("hash")
        if file_hash is None:
            continue
        hash_map.setdefault(file_hash, []).append(path)
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def find_empty_files(index: Dict[Path, dict]) -> List[Path]:
    return [path for path, meta in index.items() if meta["size"] == 0]


def find_temporary_files(index: Dict[Path, dict], temp_patterns: List[str]) -> List[Path]:
    return [
        path for path in index
        if any(fnmatch.fnmatch(path.name, pattern) for pattern in temp_patterns)
    ]


def find_name_conflicts(index: Dict[Path, dict]) -> Dict[str, List[Path]]:
    name_map: Dict[str, List[Path]] = {}
    for path in index:
        name_map.setdefault(path.name, []).append(path)
    return {name: paths for name, paths in name_map.items() if len(paths) > 1}


def find_bad_permissions(index: Dict[Path, dict], target_permissions: int) -> List[Path]:
    return [
        path for path, meta in index.items()
        if meta["permissions"] != target_permissions
    ]


def find_suspicious_names(index: Dict[Path, dict], suspicious_chars: List[str]) -> List[Path]:
    char_set = set(suspicious_chars)
    return [path for path in index if _has_suspicious_chars(path.name, char_set)]


def find_missing_files(base: Path, sources: List[Path], index: Dict[Path, dict]) -> List[Path]:
    base_names = {path.name for path in index if _is_relative_to(path, base)}
    return [
        path for path in index
        if _is_in_sources(path, sources) and path.name not in base_names
    ]


def _has_suspicious_chars(filename: str, char_set: Set[str]) -> bool:
    return any(char in filename for char in char_set)


def _is_in_sources(path: Path, sources: List[Path]) -> bool:
    return any(_is_relative_to(path, source) for source in sources)

def _is_relative_to(path: Path, other: Path) -> bool:
    try:
        path.relative_to(other)
        return True
    except ValueError:
        return False
