#!/data/data/com.termux/files/usr/bin/bash
set -eu

TARGET=/data/data/com.termux/files/home/dev/cori/research/thalean_mechanics/papers/01-unit-action-and-finite-geometric-emergence
PAPER_DIR="$TARGET/paper"
DIST_DIR="$TARGET/dist"
ZIP_NAME=unit-action-finite-geometric-emergence-overleaf.zip
OUT="$DIST_DIR/$ZIP_NAME"

if [ ! -f "$PAPER_DIR/main.tex" ]; then
  printf '%s\n' "ERROR: missing $PAPER_DIR/main.tex"
  exit 1
fi

for REQUIRED in \
  preamble.tex \
  macros.tex \
  refs.bib \
  frontmatter/abstract.tex \
  sections/01-introduction.tex \
  sections/02-unit-action.tex \
  sections/03-generated-incidence.tex \
  sections/04-visible-return-and-receipt.tex \
  sections/05-theorem-boundary.tex \
  sections/06-conclusion.tex \
  appendices/app-a-finite-cyclic-realization.tex
do
  if [ ! -f "$PAPER_DIR/$REQUIRED" ]; then
    printf '%s\n' "ERROR: missing $PAPER_DIR/$REQUIRED"
    exit 1
  fi
done

mkdir -p "$DIST_DIR"

if [ -f "$OUT" ]; then
  mv "$OUT" "$OUT.previous"
  printf '%s\n' "PREVIOUS_ARCHIVE: $OUT.previous"
fi

cd "$PAPER_DIR"

zip -9 -r "$OUT" . \
  -x '*.aux' \
  -x '*.bbl' \
  -x '*.blg' \
  -x '*.fdb_latexmk' \
  -x '*.fls' \
  -x '*.log' \
  -x '*.out' \
  -x '*.pdf' \
  -x '*.synctex.gz' \
  -x '*.toc' \
  -x '.DS_Store' \
  -x 'build/*' \
  -x 'dist/*'

zip -T "$OUT"

cd "$DIST_DIR"
sha256sum "$ZIP_NAME" > "$ZIP_NAME.sha256"

printf '%s\n' "OUT =="
printf '%s\n' "OVERLEAF_ZIP: $OUT"
printf '%s\n' "SHA256_FILE: $OUT.sha256"
printf '%s\n' "ZIP_BYTES: $(stat -c %s "$OUT")"
printf '%s\n' "ZIP_TEST_PASS: true"
printf '%s\n' "ARCHIVE_CONTENTS:"
unzip -Z1 "$OUT" | sort
