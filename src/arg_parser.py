import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="FileCurator — scan, inspect and clean file collections across directories."
    )

    parser.add_argument(
        "-X", "--base",
        metavar="BASE",
        required=True,
        help="Main directory where all files should ultimately live."
    )
    parser.add_argument(
        "sources",
        nargs="+",
        metavar="SOURCE",
        help="Additional directories to scan for missing or duplicate files."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview all actions without applying any changes."
    )
    parser.add_argument(
        "--warnings",
        action="store_true",
        help="Show warnings for inaccessible files and directories."
    )

    # --- actions ---
    parser.add_argument("--all",                  action="store_true", help="Run all inspections and apply all actions.")
    parser.add_argument("--remove-duplicates",    action="store_true", help="Find and remove duplicate files, keeping the oldest.")
    parser.add_argument("--remove-empty",         action="store_true", help="Find and delete empty files.")
    parser.add_argument("--remove-temporary",     action="store_true", help="Find and delete temporary files.")
    parser.add_argument("--copy-missing",         action="store_true", help="Copy files missing from base directory.")
    parser.add_argument("--move-missing",         action="store_true", help="Move files missing from base directory (instead of copying).")
    parser.add_argument("--resolve-conflicts",    action="store_true", help="Resolve files with the same name across directories.")
    parser.add_argument("--fix-permissions",      action="store_true", help="Fix files with non-standard permissions.")
    parser.add_argument("--fix-suspicious-names", action="store_true", help="Rename files containing suspicious characters.")

    return parser.parse_args()