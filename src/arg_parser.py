''' This file DEFINES the command-line ARGUMENTS and options for the program.'''

import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "File Cleaner - A tool to scan and clean up directory structures.\n"
            "Finds duplicates, missing files, empty/temporary files, and fixes permissions/names."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Core path arguments
    group_paths = parser.add_argument_group("File path arguments")
    group_paths.add_argument(
        "-b", "--base",
        metavar="BASE",
        required=True,
        help="The primary directory (destination for missing files)."
    )
    group_paths.add_argument(
        "sources",
        nargs="+",
        metavar="SOURCE",
        help="One or more source/backup directories to scan."
    )

    # Execution control
    group_ctrl = parser.add_argument_group("Execution control")
    group_ctrl.add_argument(
        "-dr", "--dry-run",
        action="store_true",
        help="Show what would be done without making changes."
    )
    group_ctrl.add_argument(
        "-w", "--warnings",
        action="store_true",
        help="Enable more detailed warning messages."
    )

    # Action flags
    group_actions = parser.add_argument_group("Cleanup actions")
    group_actions.add_argument(
        "-a", "--all",
        action="store_true",
        help="Run all available checks."
    )
    group_actions.add_argument(
        "-d", "--remove-duplicates",
        action="store_true",
        help="Remove identical files (keeps oldest)."
    )
    group_actions.add_argument(
        "-e", "--remove-empty",
        action="store_true",
        help="Delete empty (0-byte) files."
    )
    group_actions.add_argument(
        "-t", "--remove-temporary",
        action="store_true",
        help="Delete temporary files based on patterns in config."
    )
    group_actions.add_argument(
        "-c", "--copy-missing",
        action="store_true",
        help="Copy missing files from SOURCE to BASE."
    )
    group_actions.add_argument(
        "-m", "--move-missing",
        action="store_true",
        help="Move missing files from SOURCE to BASE (removes source)."
    )
    group_actions.add_argument(
        "-r", "--resolve-conflicts",
        action="store_true",
        help="Resolve name conflicts between different locations."
    )
    group_actions.add_argument(
        "-p", "--fix-permissions",
        action="store_true",
        help="Sync file permissions with the target value in config."
    )
    group_actions.add_argument(
        "-s", "--fix-suspicious-names",
        action="store_true",
        help="Rename files with shell-unsafe characters."
    )

    return parser.parse_args()