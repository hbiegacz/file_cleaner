import hashlib
import stat
import logging
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class FileInfo:
    path: Path
    size: int
    modified_at: float
    permissions: int
    warnings: bool = False
    _hash: Optional[str] = field(default=None, repr=False)

    @property
    def hash(self) -> Optional[str]:
        if self._hash is None:
            self._hash = self.compute_hash()
        return self._hash

    def compute_hash(self, chunk_size: int = 4096) -> Optional[str]:
        hasher = hashlib.sha256()
        try:
            with self.path.open("rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except OSError:
            if self.warnings:
                logger.warning(f"[WARN] Could not read '{self.path}', skipping hash.")
            return None


def scan_directories(directories: List[Path], ignored_dirs: List[str], warnings: bool) -> List[FileInfo]:
    files = []
    ignored_set = set(ignored_dirs)
    for directory in directories:
        if not directory.exists():
            logger.warning(f"[WARN] Directory '{directory}' does not exist, skipping.")
            continue
        files.extend(_collect_files_efficiently(directory, ignored_set, warnings))
    return files


def _collect_files_efficiently(root: Path, ignored_dirs: set, warnings: bool) -> List[FileInfo]:
    collected = []
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune ignored directories in-place to prevent os.walk from visiting them
        dirnames[:] = [d for d in dirnames if d not in ignored_dirs]
        
        for f in filenames:
            path = Path(dirpath) / f
            info = _get_file_info(path, warnings)
            if info:
                collected.append(info)
    return collected


def _get_file_info(path: Path, warnings: bool) -> Optional[FileInfo]:
    try:
        file_stat = path.stat()
        return FileInfo(
            path=path,
            size=file_stat.st_size,
            modified_at=file_stat.st_mtime,
            permissions=stat.S_IMODE(file_stat.st_mode),
            warnings=warnings
        )
    except OSError:
        if warnings:
            logger.warning(f"[WARN] Could not stat '{path}', skipping.")
        return None