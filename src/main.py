from scanner import build_file_index, scan_directories
from settings import load_settings, parse_permissions
from arg_parser import parse_arguments
from pathlib import Path
from inspector import *
from executor import *

def main():
    args = parse_arguments()
    settings = load_settings()

    base = Path(args.base)
    sources = [Path(s) for s in args.sources]

    print(f"[OK] Scanning base: {base} and sources: {sources}")
    files = build_file_index(
        scan_directories([base] + sources, settings["IGNORED_DIRS"], args.warnings),
        args.warnings
    )

    if args.all or args.remove_empty:
        print("\n\n[REMOVE EMPTY FILES]")
        empty = find_empty_files(files)
        delete_files(empty, args.dry_run)

    if args.all or args.remove_temporary:
        print("\n\n[REMOVE TEMPORARY FILES]")
        temp = find_temporary_files(files, settings["TEMP_FILE_PATTERNS"])
        delete_files(temp, args.dry_run)

    if args.all or args.remove_duplicates: 
        print("\n\n[REMOVE DUPLICATE FILES]")
        duplicates = find_duplicates(files)
        resolve_duplicates(duplicates, settings["KEEP_DUPLICATE_STRATEGY"], args.dry_run)

    if args.all or args.resolve_conflicts:
        print("\n\n[RESOLVE NAME CONFLICTS]")
        conflicts = find_name_conflicts(files)
        resolve_name_conflict(conflicts, settings["KEEP_SAME_NAME_STRATEGY"], args.dry_run)

    if args.all or args.fix_permissions:
        print("\n\n[FIX PERMISSIONS]")
        target_permissions = parse_permissions(settings["TARGET_PERMISSIONS"])
        bad_perms = find_bad_permissions(files, target_permissions)
        fix_permissions(bad_perms, target_permissions, args.dry_run)

    if args.all or args.fix_suspicious_names:
        print("\n\n[FIX SUSPICIOUS FILE NAMES]")
        suspicious = find_suspicious_names(files, settings["SUSPICIOUS_CHARS"])
        rename_file(suspicious, settings["SUSPICIOUS_CHARS"], settings["SUSPICIOUS_CHAR_SUBSTITUTE"], args.dry_run)

    if args.all or args.copy_missing:
        print("\n\n[COPY MISSING FILES TO BASE]")
        missing = find_missing_files(base, sources, files)
        copy_missing_to_base(missing,  sources, base, args.dry_run)

    if args.move_missing:
        print("\n\n[MOVE MISSING FILES TO BASE]")
        missing = find_missing_files(base, sources, files)
        move_file_to_base(missing, sources, base, args.dry_run)


if __name__ == "__main__":
    main()