import hashlib
import stat
from pathlib import Path
from typing import List, Dict, Union, Optional


def scan_directories(directories: List[Path], ignored_dirs: List[str], warnings: bool) -> List[Path]:
    files = []
    for directory in directories:
        if not directory.exists():
            if warnings:
                print(f"[WARN] Scanner: directory '{directory}' does not exist, skipping.")
            continue
        files.extend(_collect_files(directory, ignored_dirs, warnings))
    return files


def compute_file_hash(path: Path, warnings: bool, chunk_size: int = 4096) -> Optional[str]:
    hasher = hashlib.sha256()
    try:
        with path.open("rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except OSError:
        if warnings:
            print(f"[WARN] Scanner: could not read '{path}', skipping hash.")
        return None


def build_file_index(files: List[Path], warnings: bool) -> Dict[Path, dict]:
    index = {}
    for path in files:
        entry = _get_file_metadata(path, warnings)
        if entry is not None:
            index[path] = entry
    return index


# --- helpers ---

def _collect_files(directory: Path, ignored_dirs: List[str], warnings: bool) -> List[Path]:
    files = []
    for path in directory.rglob("*"):
        if _is_ignored(path, ignored_dirs):
            continue
        if path.is_file():
            files.append(path)
    return files


def _is_ignored(path: Path, ignored_dirs: List[str]) -> bool:
    return any(part in ignored_dirs for part in path.parts)


def _get_file_metadata(path: Path, warnings: bool) -> Optional[dict]:
    try:
        file_stat = path.stat()
        return {
            "size":        file_stat.st_size,
            "modified_at": file_stat.st_mtime,
            "permissions": stat.S_IMODE(file_stat.st_mode),
            "hash":        compute_file_hash(path, warnings),
        }
    except OSError:
        if warnings:
            print(f"[WARN] Scanner: could not stat '{path}', skipping.")
        return None