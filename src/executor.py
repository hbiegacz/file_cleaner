import shutil
from pathlib import Path


def delete_files(files: list[Path], dry_run: bool) -> None:
    for path in files:
        _execute(path, "delete", dry_run, _delete_file)


def copy_missing_to_base(missing: list[Path], source_roots: list[Path], base: Path, dry_run: bool) -> None:
    for path in missing:
        target = _resolve_target(path, source_roots, base)
        if target is None:
            print(f"[WARN] Could not resolve target path for '{path}', skipping.")
            continue
        _execute(path, f"copy → {target}", dry_run, lambda p, t=target: _copy_file(p, t))


def move_file_to_base(missing: list[Path], source_roots: list[Path], base: Path, dry_run: bool) -> None:
    for path in missing:
        target = _resolve_target(path, source_roots, base)
        if target is None:
            print(f"[WARN] Could not resolve target path for '{path}', skipping.")
            continue
        _execute(path, f"move → {target}", dry_run, lambda p, t=target: _move_file(p, t))


def rename_file(files: list[Path], suspicious_chars: list[str], substitute: str, dry_run: bool) -> None:
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


def fix_permissions(files: list[Path], target_permissions: int, dry_run: bool) -> None:
    for path in files:
        _execute(path, f"chmod → {oct(target_permissions)}", dry_run,
                 lambda p, perms=target_permissions: p.chmod(perms))


def resolve_duplicates(groups: dict[str, list[Path]], strategy: str, dry_run: bool) -> None:
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


def resolve_name_conflict(groups: dict[str, list[Path]], dry_run: bool) -> None:
    for name, paths in groups.items():
        try:
            sorted_paths = sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)
        except OSError as e:
            print(f"[WARN] Could not sort conflict group '{name}': {e}")
            continue

        newest = sorted_paths[0]
        others = sorted_paths[1:]

        print(f"\n[INFO] Conflict '{name}' — keeping newest: {newest}")
        for p in others:
            print(f"       older: {p}")

        policy = input("Remove older files? [(a)ll / (s)ome / (N)one]: ").strip().lower()

        if policy == "a":
            delete_files(others, dry_run)
        elif policy == "s":
            _ask_per_file(others, dry_run)


def skip_file(files: list[Path]) -> None:
    for path in files:
        print(f"[INFO] Skipped (no action): '{path}'")


def apply_batch_policy(files: list[Path], policy: str, dry_run: bool, **kwargs) -> None:
    actions = {
        "delete": lambda: delete_files(files, dry_run),
        "skip":   lambda: skip_file(files),
        "copy":   lambda: copy_missing_to_base(files, kwargs["source_roots"], kwargs["base"], dry_run),
        "move":   lambda: move_file_to_base(files, kwargs["source_roots"], kwargs["base"], dry_run),
    }
    action = actions.get(policy)
    if action is None:
        print(f"[ERROR] Unknown batch policy '{policy}', skipping.")
        return
    action()


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


def _resolve_target(path: Path, source_roots: list[Path], base: Path) -> Path | None:
    for root in source_roots:
        try:
            relative = path.relative_to(root)
            return base / relative
        except ValueError:
            continue
    return None


def _sanitize_name(name: str, char_set: set[str], substitute: str) -> str:
    return "".join(substitute if c in char_set else c for c in name)


def _ask_per_file(files: list[Path], dry_run: bool) -> None:
    for path in files:
        answer = input(f"  Remove '{path}'? [y/N]: ").strip().lower()
        if answer == "y":
            delete_files([path], dry_run)