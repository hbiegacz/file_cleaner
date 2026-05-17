''' This file contains functions to PERFORM file OPERATIONS like delete, copy, move, rename or fix permissions.'''

import shutil
import logging
from pathlib import Path
from typing import List, Dict, Optional, Set, Callable, Any

logger = logging.getLogger(__name__)

def delete_files(files: List[Path], dry_run: bool) -> None:
    for path in files:
        _execute(path, "delete", dry_run, lambda p: p.unlink())


def copy_missing_to_base(missing: List[Path], source_roots: List[Path], base: Path, dry_run: bool) -> None:
    for path in missing:
        target = _resolve_target(path, source_roots, base)
        if target:
            _execute(path, f"copy -> {target}", dry_run, lambda p, t=target: _copy_file(p, t))
        else:
            logger.warning(f"[WARN] Could not resolve target path for '{path}', skipping.")


def move_file_to_base(missing: List[Path], source_roots: List[Path], base: Path, dry_run: bool) -> None:
    for path in missing:
        target = _resolve_target(path, source_roots, base)
        if target:
            _execute(path, f"move -> {target}", dry_run, lambda p, t=target: _move_file(p, t))
        else:
            logger.warning(f"[WARN] Could not resolve target path for '{path}', skipping.")


def rename_file(files: List[Path], suspicious_chars: List[str], substitute: str, dry_run: bool) -> None:
    char_set = set(suspicious_chars)
    for path in files:
        new_name = "".join(substitute if c in char_set else c for c in path.name)
        new_path = path.parent / new_name
        if new_path == path:
            continue
        if new_path.exists():
            logger.warning(f"[WARN] Skipped rename '{path.name}' -> '{new_name}': target already exists.")
            continue
        _execute(path, f"rename -> {new_name}", dry_run, lambda p, t=new_path: p.rename(t))


def fix_permissions(files: List[Path], target_permissions: int, dry_run: bool) -> None:
    for path in files:
        _execute(path, f"chmod -> {oct(target_permissions)}", dry_run, lambda p: p.chmod(target_permissions))


def resolve_conflicts(groups: Dict[str, List[Path]], strategy: str, dry_run: bool, label: str = "conflict") -> None:
    """Generic resolver for duplicate content or name conflicts."""
    for key, paths in groups.items():
        try:
            # For duplicates, we might want oldest/newest.
            # strategy: 'oldest' means keep the one with smallest mtime.
            # strategy: 'newest' means keep the one with largest mtime.
            reverse = (strategy == "newest")
            sorted_paths = sorted(paths, key=lambda p: p.stat().st_mtime, reverse=reverse)
        except OSError as e:
            logger.error(f"[ERROR] Could not sort {label} group '{key}': {e}")
            continue

        keep = sorted_paths[0]
        to_delete = sorted_paths[1:]

        logger.info(f"{label.capitalize()} '{key}' — keeping {strategy}: {keep}")
        for p in to_delete:
            logger.info(f"  removing: {p}")
        
        delete_files(to_delete, dry_run)


# --- helpers ---

def _execute(path: Path, action_label: str, dry_run: bool, action: Callable[[Path], Any]) -> None:
    if dry_run:
        logger.info(f"[DRY-RUN] Would {action_label}: '{path}'")
        return
    try:
        action(path)
        logger.info(f"[OK] {action_label}: '{path}'")
    except OSError as e:
        logger.error(f"[ERROR] Could not execute on '{path}': {e}")


def _copy_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def _move_file(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source), target)


def _resolve_target(path: Path, source_roots: List[Path], base: Path) -> Optional[Path]:
    for root in source_roots:
        try:
            relative = path.relative_to(root)
            return base / relative
        except ValueError:
            continue
    return None
