#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAPER="$ROOT/paper"
DIST="$ROOT/dist"
ZIP="$DIST/finite-covariant-receipt-algebra-on-graphs-overleaf.zip"
SHA="$ZIP.sha256"

mkdir -p "$DIST"

echo "PROGRESS: [1/4] checking source tree"
for item in main.tex preamble.tex macros.tex refs.bib latexmkrc frontmatter sections appendices; do
    test -e "$PAPER/$item"
done

echo "PROGRESS: [2/4] creating source-only Overleaf archive"
cd "$PAPER"
zip -q -r -FS "$ZIP" \
    main.tex preamble.tex macros.tex refs.bib latexmkrc \
    frontmatter sections appendices \
    -x '*.aux' '*.bbl' '*.bcf' '*.blg' '*.fdb_latexmk' '*.fls' '*.log' '*.out' '*.pdf' '*.run.xml' '*.synctex.gz'

echo "PROGRESS: [3/4] testing archive"
unzip -t "$ZIP" >/dev/null

echo "PROGRESS: [4/4] writing checksum"
sha256sum "$ZIP" > "$SHA"

echo "OUT =="
echo "OVERLEAF_ZIP: $ZIP"
echo "SHA256_FILE: $SHA"
echo "ZIP_BYTES: $(wc -c < "$ZIP" | tr -d ' ')"
echo "ZIP_TEST_PASS: true"
echo "LATEX_BUILD_SKIPPED: true"
echo "ARCHIVE_CONTENTS:"
unzip -Z1 "$ZIP"
