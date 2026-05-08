import fnmatch
from pathlib import Path
from typing import List, Dict, Set, Optional
from scanner import FileInfo


def find_duplicates(files: List[FileInfo]) -> Dict[str, List[Path]]:
    hash_map: Dict[str, List[Path]] = {}
    for info in files:
        file_hash = info.hash  # This triggers lazy computation if needed
        if file_hash is None:
            continue
        hash_map.setdefault(file_hash, []).append(info.path)
    return {h: paths for h, paths in hash_map.items() if len(paths) > 1}


def find_empty_files(files: List[FileInfo]) -> List[Path]:
    return [info.path for info in files if info.size == 0]


def find_temporary_files(files: List[FileInfo], temp_patterns: List[str]) -> List[Path]:
    return [
        info.path for info in files
        if any(fnmatch.fnmatch(info.path.name, pattern) for pattern in temp_patterns)
    ]


def find_name_conflicts(files: List[FileInfo]) -> Dict[str, List[Path]]:
    name_map: Dict[str, List[Path]] = {}
    for info in files:
        name_map.setdefault(info.path.name, []).append(info.path)
    return {name: paths for name, paths in name_map.items() if len(paths) > 1}


def find_bad_permissions(files: List[FileInfo], target_permissions: int) -> List[Path]:
    return [
        info.path for info in files
        if info.permissions != target_permissions
    ]


def find_suspicious_names(files: List[FileInfo], suspicious_chars: List[str]) -> List[Path]:
    char_set = set(suspicious_chars)
    return [info.path for info in files if _has_suspicious_chars(info.path.name, char_set)]


def find_missing_files(base: Path, sources: List[Path], files: List[FileInfo]) -> List[Path]:
    base_names = {info.path.name for info in files if _is_relative_to(info.path, base)}
    return [
        info.path for info in files
        if _is_in_sources(info.path, sources) and info.path.name not in base_names
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
