#!/bin/bash

# Creates test directory structure
# Usage: bash create_test_data.sh (run from project root)

BASE="test_data/base"
Y1="test_data/source1"
Y2="test_data/source2"

echo "Creating test directory structure..."
mkdir -p "$BASE"/{documents,photos,misc} \
         "$Y1"/{docs/old/archived,media/photos} \
         "$Y2"/{super/deep/dir/structure,backup}

# ---------------------------------------------------------------
# duplicate content 
# ---------------------------------------------------------------
echo "duplicate content" > "$BASE/documents/report.txt"
echo "duplicate content" > "$Y1/docs/old/report_copy.txt"
echo "duplicate content" > "$Y2/backup/report_backup.txt"

# ---------------------------------------------------------------
# missing files — present in Y1/Y2 but not in X
# ---------------------------------------------------------------
echo "only in source1"   > "$Y1/docs/only_in_source1.txt"
echo "deep nested file"  > "$Y2/super/deep/dir/structure/deep_file.txt"
echo "another missing"   > "$Y2/backup/another_missing.txt"

# ---------------------------------------------------------------
# name conflict — same filename, different content/location
# ---------------------------------------------------------------
echo "older version" > "$BASE/documents/notes.txt"
sleep 1
echo "newer version" > "$Y1/docs/old/notes.txt"

# ---------------------------------------------------------------
# empty files
# ---------------------------------------------------------------
touch "$BASE/misc/empty_file.txt"
touch "$Y1/docs/also_empty.txt"

# ---------------------------------------------------------------
# temporary files
# ---------------------------------------------------------------
echo "tmp content"   > "$BASE/misc/session.tmp"
echo "vim swap"      > "$BASE/documents/report.txt~"
echo "backup file"   > "$Y1/docs/old/archived/notes.bak"

# ---------------------------------------------------------------
# suspicious characters in filenames
# ---------------------------------------------------------------
echo "fake jpg content 1" > "$BASE/photos/my photo 2024.jpg"
echo "fake pdf content"   > "$BASE/photos/scan;final.pdf"
echo "fake jpg content 2" > "$Y1/media/photos/holiday photo #1.jpg"
echo "fake txt content"   > "$Y2/super/deep/dir/structure/file with spaces & symbols.txt"

# ---------------------------------------------------------------
# bad permissions
# ---------------------------------------------------------------
echo "wrong perms"      > "$BASE/misc/restricted.txt"
chmod 777 "$BASE/misc/restricted.txt"

echo "also wrong"       > "$Y1/docs/executable_doc.txt"
chmod 755 "$Y1/docs/executable_doc.txt"

# ---------------------------------------------------------------
# duplicate content in deep structure
# ---------------------------------------------------------------
echo "nested duplicate" > "$BASE/misc/config.cfg"
echo "nested duplicate" > "$Y2/super/deep/dir/structure/config.cfg"

echo ""
echo "Done. Test structure:"
tree test_data