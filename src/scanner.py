import hashlib
import stat
from pathlib import Path


def scan_directories(directories: list[Path], ignored_dirs: list[str], warnings: bool) -> list[Path]:
    files = []
    for directory in directories:
        if not directory.exists():
            if warnings:
                print(f"[WARN] Scanner: directory '{directory}' does not exist, skipping.")
            continue
        files.extend(_collect_files(directory, ignored_dirs, warnings))
    return files


def compute_file_hash(path: Path, warnings: bool, chunk_size: int = 4096) -> str | None:
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


def build_file_index(files: list[Path], warnings: bool) -> dict[Path, dict]:
    index = {}
    for path in files:
        entry = _get_file_metadata(path, warnings)
        if entry is not None:
            index[path] = entry
    return index


# --- helpers ---

def _collect_files(directory: Path, ignored_dirs: list[str], warnings: bool) -> list[Path]:
    files = []
    for path in directory.rglob("*"):
        if _is_ignored(path, ignored_dirs):
            continue
        if path.is_file():
            files.append(path)
    return files


def _is_ignored(path: Path, ignored_dirs: list[str]) -> bool:
    return any(part in ignored_dirs for part in path.parts)


def _get_file_metadata(path: Path, warnings: bool) -> dict | None:
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