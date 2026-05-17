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
echo "deep nested file only in source2"  > "$Y2/super/deep/dir/structure/deep_file.txt"
echo "another missing only in source2"   > "$Y2/backup/another_missing.txt"

# ---------------------------------------------------------------
# name conflict — same filename, different content/location
# ---------------------------------------------------------------
echo "duplicate name - older version" > "$BASE/documents/notes.txt"
sleep 1
echo "duplicate name - newer version" > "$Y1/docs/old/notes.txt"

# ---------------------------------------------------------------
# empty files
# ---------------------------------------------------------------
touch "$BASE/misc/empty_file.txt"
touch "$Y1/docs/also_empty.txt"

# ---------------------------------------------------------------
# temporary files
# ---------------------------------------------------------------
echo "temp content"   > "$BASE/misc/session.tmp"
echo "temp vim swap"      > "$BASE/documents/report.txt~"
echo "temp backup file"   > "$Y1/docs/old/archived/notes.bak"

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
echo "wrong permsissions"      > "$BASE/misc/restricted.txt"
chmod 777 "$BASE/misc/restricted.txt"

echo "also wrong permissions"       > "$Y1/docs/executable_doc.txt"
chmod 755 "$Y1/docs/executable_doc.txt"

# ---------------------------------------------------------------
# duplicate content in deep structure
# ---------------------------------------------------------------
echo "nested duplicate" > "$BASE/misc/config.cfg"
echo "super nested duplicate" > "$Y2/super/deep/dir/structure/config.cfg"

echo "Done. "
echo ""
echo "If you have Tree installed, you can use the following command to see the structure more clearly:"
echo "tree test_data"
echo "You can also use:"
echo "ls test_data --recursive"
