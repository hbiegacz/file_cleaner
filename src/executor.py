import shutil
from pathlib import Path
from typing import List, Dict, Set, Optional


def delete_files(files: List[Path], dry_run: bool) -> None:
    for path in files:
        _execute(path, "delete", dry_run, _delete_file)


def copy_missing_to_base(missing: List[Path], source_roots: List[Path], base: Path, dry_run: bool) -> None:
    for path in missing:
        target = _resolve_target(path, source_roots, base)
        if target is None:
            print(f"[WARN] Could not resolve target path for '{path}', skipping.")
            continue
        _execute(path, f"copy → {target}", dry_run, lambda p, t=target: _copy_file(p, t))


def move_file_to_base(missing: List[Path], source_roots: List[Path], base: Path, dry_run: bool) -> None:
    for path in missing:
        target = _resolve_target(path, source_roots, base)
        if target is None:
            print(f"[WARN] Could not resolve target path for '{path}', skipping.")
            continue
        _execute(path, f"move → {target}", dry_run, lambda p, t=target: _move_file(p, t))


def rename_file(files: List[Path], suspicious_chars: List[str], substitute: str, dry_run: bool) -> None:
    char_set = set(suspicious_chars)
    for path in files:
        new_name = _sanitize_name(path.name, char_set, substitute)
        new_path = path.parent / new_name
        if new_path == path:
            continue
        if new_path.exists():
            print(f"[WARN] Skipped rename '{path.name}' → '{new_name}': target already exists.")
            continue
        _execute(path, f"rename → {new_name}", dry_run, lambda p, t=new_path: p.rename(t))


def fix_permissions(files: List[Path], target_permissions: int, dry_run: bool) -> None:
    for path in files:
        _execute(path, f"chmod → {oct(target_permissions)}", dry_run,
                 lambda p, perms=target_permissions: p.chmod(perms))


def resolve_duplicates(groups: Dict[str, List[Path]], strategy: str, dry_run: bool) -> None:
    for file_hash, paths in groups.items():
        try:
            sorted_paths = sorted(paths, key=lambda p: p.stat().st_mtime)
        except OSError as e:
            print(f"[WARN] Could not sort duplicate group: {e}")
            continue

        keep = sorted_paths[0] if strategy == "oldest" else sorted_paths[-1]
        to_delete = [p for p in sorted_paths if p != keep]

        print(f"[INFO] Keeping '{keep}' ({strategy}), removing {len(to_delete)} duplicate(s).")
        delete_files(to_delete, dry_run)


def resolve_name_conflict(groups: Dict[str, List[Path]], strategy: str, dry_run: bool) -> None:
    for name, paths in groups.items():
        try:
            sorted_paths = sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)
        except OSError as e:
            print(f"[WARN] Could not sort conflict group '{name}': {e}")
            continue

        keep = sorted_paths[0] if strategy == "newest" else sorted_paths[-1]
        to_delete = [p for p in sorted_paths if p != keep]

        print(f"[INFO] Conflict '{name}' — keeping {strategy}: {keep}")
        for p in to_delete:
            print(f"       removing: {p}")

        delete_files(to_delete, dry_run)


# --- helpers ---

def _execute(path: Path, action_label: str, dry_run: bool, action) -> None:
    if dry_run:
        print(f"[DRY-RUN] Would {action_label}: '{path}'")
        return
    try:
        action(path)
        print(f"[OK] {action_label}: '{path}'")
    except OSError as e:
        print(f"[ERROR] Could not execute on '{path}': {e}")


def _delete_file(path: Path) -> None:
    path.unlink()


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


def _sanitize_name(name: str, char_set: Set[str], substitute: str) -> str:
    return "".join(substitute if c in char_set else c for c in name)
