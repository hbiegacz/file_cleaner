# File Cleaner
![Bash](https://img.shields.io/badge/gnu-bash-00000?style=for-the-badge&logo=gnubash&logoSize=auto) ![Python](https://img.shields.io/badge/python-00000?style=for-the-badge&logo=python&logoSize=auto&labelColor=gold&color=gold)

A command-line tool for organizing large file collections spread across multiple directories.
Finds duplicates, missing files, empty/temporary files, name conflicts and permission issues - then suggests or applies the appropriate fix.
Project created for the course _Administrowanie Systemem UNIX i siecią TCP/IP_ (ASU).

## Usage

```bash
python src/main.py -b <BASE> <SOURCE> [SOURCE ...] [options]
```

`BASE` is the main directory where all files should end up.
`SOURCE` is one or more directories to scan alongside it.

## Options

| Flag | Short | Description |
|---|---|---|
| `--all` | `-a` | Run all checks |
| `--remove-duplicates` | `-d` | Remove duplicate files, keeping the oldest |
| `--remove-empty` | `-e` | Delete empty files (0 bytes) |
| `--remove-temporary` | `-t` | Delete temporary files (*.tmp, *~, *.bak) |
| `--copy-missing` | `-c` | Copy files missing from BASE |
| `--move-missing` | `-m` | Move files missing from BASE |
| `--resolve-conflicts` | `-r` | Interactively resolve files with the same name |
| `--fix-permissions` | `-p` | Fix files with wrong permissions |
| `--fix-suspicious-names` | `-s` | Rename files with problematic characters |
| `--dry-run` | `-dr` | Preview actions without applying any changes |
| `--warnings` | `-w` | Show warnings for inaccessible files |

## Examples

```bash
# preview all checks without changing anything
python src/main.py -b ~/documents ~/backup1 ~/backup2 --all --dry-run

# remove duplicates and empty files
python src/main.py -b ~/documents ~/backup1 --remove-duplicates --remove-empty --warnings

# copy missing files and fix permissions
python src/main.py -b ~/documents ~/backup1 ~/backup2 -c -p 
```

## Configuration

Settings are loaded from `.clean_files` in the project directory.
If the file does not exist, defaults are used.

```json
{
  "TARGET_PERMISSIONS": "rw-r--r--",
  "SUSPICIOUS_CHARS": [" ", "'", "\"", ",", ";", "*", "?", "$", "#", "&", "|", "\\"],
  "SUSPICIOUS_CHAR_SUBSTITUTE": "_",
  "TEMP_FILE_PATTERNS": ["*.tmp", "*~", "*.bak"],
  "DRY_RUN": true,
  "KEEP_DUPLICATE_STRATEGY": "oldest",
  "IGNORED_DIRS": [".git", "__pycache__", ".DS_Store", "node_modules", ".idea"]
}
```

## Test data

To generate a set of test directories covering all supported cases:

```bash
bash create_test_dirs.sh
python src/main.py -b test_data/base test_data/source1 test_data/source2 --all --dry-run
```
