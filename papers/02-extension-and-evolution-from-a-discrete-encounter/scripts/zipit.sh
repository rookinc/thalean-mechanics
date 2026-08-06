#!/data/data/com.termux/files/usr/bin/bash
set -eu
TARGET=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PAPER=$TARGET/paper
DIST=$TARGET/dist
OUT=$DIST/extension-evolution-discrete-encounter-overleaf.zip
mkdir -p $DIST
cd $PAPER
zip -9 -r $OUT . -x '*.aux' '*.bbl' '*.blg' '*.log' '*.out' '*.pdf' '*.toc'
zip -T $OUT
cd $DIST
sha256sum extension-evolution-discrete-encounter-overleaf.zip > extension-evolution-discrete-encounter-overleaf.zip.sha256
printf '%s\n' "OVERLEAF_ZIP: $OUT"
