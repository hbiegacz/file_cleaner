from scanner import build_file_index, scan_directories
from arg_parser import parse_arguments
from settings import load_settings
from pathlib import Path

def main():
    # --- load config ---
    settings = load_settings()
    print("[settings] Config loaded.")

    args = parse_arguments()
    base = Path(args.base)
    sources = [Path(s) for s in args.sources]
    dry_run = args.dry_run

    if dry_run:
        print("\n[dry-run] No changes will be applied.")

    # --- scan ---
    files = build_file_index(
        scan_directories([base] + sources, settings["IGNORED_DIRS"], args.warnings),
        args.warnings
    )
    print(f"\n[scanner] Scanning base: {base} and sources: {sources}")

    # --- inspect & execute ---

    if args.all or args.remove_empty:
        # empty = find_empty_files(files)
        # delete_files(empty, dry_run)
        print("\n[inspector] Looking for empty files...")
        print("[executor]  Deleting empty files...")

    if args.all or args.remove_temporary:
        # temp = find_temporary_files(files)
        # delete_files(temp, dry_run)
        print("\n[inspector] Looking for temporary files...")
        print("[executor]  Deleting temporary files...")

    if args.all or args.remove_duplicates:
        # duplicates = find_duplicates(files)
        # resolve_duplicates(duplicates, dry_run)
        print("\n[inspector] Looking for duplicate files...")
        print("[executor]  Resolving duplicates...")

    if args.all or args.resolve_conflicts:
        # conflicts = find_name_conflicts(files)
        # resolve_name_conflict(conflicts, dry_run)
        print("\n[inspector] Looking for name conflicts...")
        print("[executor]  Resolving name conflicts...")

    if args.all or args.fix_permissions:
        # bad_perms = find_bad_permissions(files)
        # fix_permissions(bad_perms, dry_run)
        print("\n[inspector] Looking for bad permissions...")
        print("[executor]  Fixing permissions...")

    if args.all or args.fix_suspicious_names:
        # suspicious = find_suspicious_names(files)
        # rename_file(suspicious, dry_run)
        print("\n[inspector] Looking for suspicious file names...")
        print("[executor]  Renaming files...")

    if args.all or args.copy_missing:
        # missing = find_missing_files(base, sources, files)
        # copy_missing_to_base(missing, base, dry_run)
        print("\n[inspector] Looking for files missing from base...")
        print("[executor]  Copying missing files to base...")

    if args.move_missing:
        # missing = find_missing_files(base, sources, files)
        # move_file_to_base(missing, base, dry_run)
        print("\n[inspector] Looking for files missing from base...")
        print("[executor]  Moving missing files to base...")

    print("\n[done] All tasks completed.")


if __name__ == "__main__":
    main()