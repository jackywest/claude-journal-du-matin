#!/usr/bin/env bash
# print.sh : envoie une.pdf à l'imprimante par défaut (lp). --dry-run : n'imprime rien.
# Usage : scripts/print.sh [--dry-run] [une.pdf]
set -euo pipefail
DRY=0; FILE=""
for a in "$@"; do case "$a" in --dry-run) DRY=1;; *) FILE="$a";; esac; done
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FILE="${FILE:-$DIR/une.pdf}"
[ -f "$FILE" ] || { echo "PDF introuvable : $FILE" >&2; exit 1; }
PRN="$(lpstat -d 2>/dev/null | sed -n 's/.*: *//p' | grep -v 'aucune\|no system' || true)"
if [ "$DRY" = 1 ]; then
  echo "[dry-run] commande qui serait lancée : lp -o media=A4 -o fit-to-page \"$FILE\""
  echo "[dry-run] imprimante par défaut : ${PRN:-AUCUNE (définir une imprimante par défaut dans Réglages Système > Imprimantes)}"
  echo "[dry-run] rien n'a été imprimé."
  exit 0
fi
[ -n "$PRN" ] || { echo "Aucune imprimante par défaut : rien imprimé." >&2; exit 1; }
lp -o media=A4 -o fit-to-page "$FILE"
