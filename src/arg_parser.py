import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "File Cleaner." +
            "Scans multiple directories to find duplicates, missing files, "
            "empty/temporary files, name conflicts and permission issues, then cleans them up."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "-b", "--base",
        metavar="BASE",
        required=True,
        help="The main directory where all files should end up. "
             "Missing files from SOURCE directories will be copied here."
    )
    parser.add_argument(
        "sources",
        nargs="+",
        metavar="SOURCE",
        help="One or more directories to scan alongside BASE. "
             "These are treated as backup or secondary locations."
    )
    parser.add_argument(
        "-dr", "--dry-run",
        action="store_true",
        help="Show what would be done without making any actual changes. "
             "Safe to run at any time."
    )
    parser.add_argument(
        "-w", "--warnings",
        action="store_true",
        help="Print warnings when a file or directory cannot be accessed."
    )

    parser.add_argument(
        "-a", "--all",
        action="store_true",
        help="Run all available checks and apply their actions."
    )
    parser.add_argument(
        "-d", "--remove-duplicates",
        action="store_true",
        help="Find files with identical content (regardless of name or location) "
             "and remove all copies except the oldest one."
    )
    parser.add_argument(
        "-e", "--remove-empty",
        action="store_true",
        help="Find and delete files that are completely empty (0 bytes)."
    )
    parser.add_argument(
        "-t", "--remove-temporary",
        action="store_true",
        help="Find and delete temporary files such as *.tmp, *~ and *.bak. "
             "Patterns can be changed in the config file."
    )
    parser.add_argument(
        "-c", "--copy-missing",
        action="store_true",
        help="Copy files that exist in SOURCE directories but are missing from BASE."
    )
    parser.add_argument(
        "-m", "--move-missing",
        action="store_true",
        help="Move files that exist in SOURCE directories but are missing from BASE. "
             "Unlike --copy-missing, the original file is removed after moving."
    )
    parser.add_argument(
        "-r", "--resolve-conflicts",
        action="store_true",
        help="Find files with the same name in different locations "
             "and interactively decide which ones to keep."
    )
    parser.add_argument(
        "-p", "--fix-permissions",
        action="store_true",
        help="Find files whose permissions differ from the expected value "
             "and update them. The target permissions are set in the config file."
    )
    parser.add_argument(
        "-s", "--fix-suspicious-names",
        action="store_true",
        help="Rename files whose names contain characters that may cause issues "
             "in the shell (e.g. spaces, quotes, semicolons). "
             "Problematic characters are replaced with a substitute defined in the config file."
    )

    return parser.parse_args()