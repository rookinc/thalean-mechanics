#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

TARGET="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAPER="$TARGET/paper"
DIST="$TARGET/dist"
ZIP="$DIST/parity-dihedral-receipt-tower-overleaf.zip"
SHA="$ZIP.sha256"

test -f "$PAPER/main.tex"
test -f "$PAPER/preamble.tex"
test -f "$PAPER/macros.tex"
test -f "$PAPER/refs.bib"

mkdir -p "$DIST"
rm -f "$ZIP" "$SHA"

cd "$PAPER"
zip -q -r "$ZIP" \
  main.tex \
  preamble.tex \
  macros.tex \
  refs.bib \
  latexmkrc \
  frontmatter \
  sections \
  appendices \
  -x '*.aux' '*.log' '*.out' '*.toc' '*.fls' '*.fdb_latexmk' '*.synctex.gz' '*.pdf'

unzip -t "$ZIP"
sha256sum "$ZIP" > "$SHA"

echo "OUT =="
echo "LATEX_BUILD_SKIPPED: true"
echo "OVERLEAF_ZIP: $ZIP"
echo "SHA256_FILE: $SHA"
echo "ZIP_BYTES: $(stat -c %s "$ZIP")"
echo "ZIP_TEST_PASS: true"
echo "ARCHIVE_CONTENTS:"
unzip -Z1 "$ZIP"

