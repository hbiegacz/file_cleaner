import logging
import sys
from pathlib import Path

from scanner import scan_directories
from settings import load_settings, parse_permissions
from arg_parser import parse_arguments
import inspector
import executor

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        stream=sys.stdout
    )

def main():
    args = parse_arguments()
    setup_logging()
    
    settings = load_settings()

    base = Path(args.base)
    sources = [Path(s) for s in args.sources]

    logging.info(f"Scanning base: {base} and sources: {sources}")
    files = scan_directories([base] + sources, settings["IGNORED_DIRS"], args.warnings)
    logging.info(f"Found {len(files)} files total.")

    if not files:
        logging.info("[WARN] No files found to process. Check if the directories exist and are not empty.")
        return

    if args.all or args.remove_empty:
        logging.info("\n[REMOVE EMPTY FILES]")
        empty = inspector.find_empty_files(files)
        executor.delete_files(empty, args.dry_run)

    if args.all or args.remove_temporary:
        logging.info("\n[REMOVE TEMPORARY FILES]")
        temp = inspector.find_temporary_files(files, settings["TEMP_FILE_PATTERNS"])
        executor.delete_files(temp, args.dry_run)

    if args.all or args.remove_duplicates: 
        logging.info("\n[REMOVE DUPLICATE FILES]")
        duplicates = inspector.find_duplicates(files)
        executor.resolve_conflicts(
            duplicates, 
            settings["KEEP_DUPLICATE_STRATEGY"], 
            args.dry_run, 
            label="duplicate"
        )

    if args.all or args.resolve_conflicts:
        logging.info("\n[RESOLVE NAME CONFLICTS]")
        conflicts = inspector.find_name_conflicts(files)
        executor.resolve_conflicts(
            conflicts, 
            settings["KEEP_SAME_NAME_STRATEGY"], 
            args.dry_run, 
            label="name conflict"
        )

    if args.all or args.fix_permissions:
        logging.info("\n[FIX PERMISSIONS]")
        target_permissions = parse_permissions(settings["TARGET_PERMISSIONS"])
        bad_perms = inspector.find_bad_permissions(files, target_permissions)
        executor.fix_permissions(bad_perms, target_permissions, args.dry_run)

    if args.all or args.fix_suspicious_names:
        logging.info("\n[FIX SUSPICIOUS FILE NAMES]")
        suspicious = inspector.find_suspicious_names(files, settings["SUSPICIOUS_CHARS"])
        executor.rename_file(
            suspicious, 
            settings["SUSPICIOUS_CHARS"], 
            settings["SUSPICIOUS_CHAR_SUBSTITUTE"], 
            args.dry_run
        )

    if args.all or args.copy_missing:
        logging.info("\n[COPY MISSING FILES TO BASE]")
        missing = inspector.find_missing_files(base, sources, files)
        executor.copy_missing_to_base(missing, sources, base, args.dry_run)

    if args.move_missing:
        logging.info("\n[MOVE MISSING FILES TO BASE]")
        missing = inspector.find_missing_files(base, sources, files)
        executor.move_file_to_base(missing, sources, base, args.dry_run)


if __name__ == "__main__":
    main()