#!/usr/bin/env bash
# render.sh : une.html -> une.pdf (A4, 1 page) avec Chrome en ligne de commande. Aucune dépendance à installer.
# Usage : scripts/render.sh [une.html] [une.pdf]
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
IN="${1:-$DIR/une.html}"; OUT="${2:-$DIR/une.pdf}"
CHROME="${CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"
[ -x "$CHROME" ] || { echo "Chrome introuvable ($CHROME). Définir CHROME=/chemin/vers/chrome." >&2; exit 1; }
[ -f "$IN" ] || { echo "Fichier introuvable : $IN" >&2; exit 1; }
IN_ABS="$(cd "$(dirname "$IN")" && pwd)/$(basename "$IN")"
PROFIL="$(mktemp -d)"; trap 'rm -rf "$PROFIL"' EXIT
"$CHROME" --headless=new --disable-gpu --no-sandbox --user-data-dir="$PROFIL" \
  --no-pdf-header-footer --virtual-time-budget=15000 \
  --print-to-pdf="$OUT" "file://$IN_ABS" >/dev/null 2>&1
[ -s "$OUT" ] || { echo "Le PDF n'a pas été créé." >&2; exit 1; }
PAGES="$(python3 - "$OUT" <<'PY'
import re, sys
print(len(re.findall(rb"/Type\s*/Page[^s]", open(sys.argv[1], "rb").read())))
PY
)"
echo "PDF : $OUT ($PAGES page(s))"
[ "$PAGES" = "1" ] || { echo "ATTENTION : $PAGES pages au lieu de 1 — raccourcir les textes." >&2; exit 2; }
