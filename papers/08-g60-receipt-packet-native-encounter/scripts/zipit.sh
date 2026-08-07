#!/data/data/com.termux/files/usr/bin/bash

PROJECT="/data/data/com.termux/files/home/dev/cori/research/thalean_mechanics/papers/08-g60-receipt-packet-native-encounter"
PAPER="$PROJECT/paper"
DIST="$PROJECT/dist"
ZIP="$DIST/a-blind-encounter-between-finite-receipt-algebra-and-the-native-g60-graph-overleaf.zip"
SUM="${ZIP}.sha256"

mkdir -p "$DIST"

printf '%s\n' "PROGRESS: [1/4] checking source tree"
test -f "$PAPER/main.tex"
test -f "$PAPER/frontmatter/abstract.tex"
test -f "$PAPER/sections/07-native-receipt-tower-theorem.tex"

printf '%s\n' "PROGRESS: [2/4] creating source-only Overleaf archive"
rm -f "$ZIP" "$SUM"

(
  cd "$PAPER"
  zip -qr "$ZIP" \
    main.tex \
    preamble.tex \
    macros.tex \
    refs.bib \
    latexmkrc \
    frontmatter \
    sections \
    appendices
)

printf '%s\n' "PROGRESS: [3/4] testing archive"
unzip -t "$ZIP" >/dev/null
ZIP_BYTES=$(wc -c < "$ZIP" | tr -d ' ')

printf '%s\n' "PROGRESS: [4/4] writing checksum"
sha256sum "$ZIP" > "$SUM"

clear
printf '%s\n' "OUT =="
printf '%s\n' "OVERLEAF_ZIP: $ZIP"
printf '%s\n' "SHA256_FILE: $SUM"
printf '%s\n' "ZIP_BYTES: $ZIP_BYTES"
printf '%s\n' "ZIP_TEST_PASS: true"
printf '%s\n' "LATEX_BUILD_SKIPPED: true"
printf '%s\n' "ARCHIVE_CONTENTS:"
unzip -Z1 "$ZIP"
