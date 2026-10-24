#!/usr/bin/env bash
# install-6h.sh : crée une tâche launchd macOS qui lance Claude Code chaque matin à 6 h.
# Usage : scripts/install-6h.sh [--dry-run] [--heure 6] [--minute 0]   (--uninstall pour retirer)
set -euo pipefail
DRY=0; H=6; M=0; UN=0
while [ $# -gt 0 ]; do case "$1" in
  --dry-run) DRY=1;; --heure) H="$2"; shift;; --minute) M="$2"; shift;; --uninstall) UN=1;;
  *) echo "Option inconnue : $1" >&2; exit 1;; esac; shift; done
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL="fr.jackywest.journal-du-matin"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"
CLAUDE="$(command -v claude || echo claude)"
if [ "$UN" = 1 ]; then launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true; rm -f "$PLIST"; echo "Retiré."; exit 0; fi
CONTENU="<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\"><dict>
  <key>Label</key><string>$LABEL</string>
  <key>WorkingDirectory</key><string>$DIR</string>
  <key>ProgramArguments</key><array>
    <string>$CLAUDE</string><string>-p</string><string>/journal-du-matin</string>
    <string>--permission-mode</string><string>acceptEdits</string>
    <string>--allowedTools</string><string>Bash(python3:*) Bash(bash:*) Bash(scripts/*) Read Write Edit</string>
  </array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>$H</integer><key>Minute</key><integer>$M</integer></dict>
  <key>StandardOutPath</key><string>$DIR/journal.log</string>
  <key>StandardErrorPath</key><string>$DIR/journal.log</string>
  <key>EnvironmentVariables</key><dict><key>PATH</key><string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin:$HOME/.local/bin</string></dict>
</dict></plist>"
if [ "$DRY" = 1 ]; then echo "[dry-run] fichier : $PLIST"; echo "$CONTENU"; echo "[dry-run] rien n'a été installé."; exit 0; fi
mkdir -p "$(dirname "$PLIST")"; echo "$CONTENU" > "$PLIST"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installé : chaque jour à $(printf '%02d:%02d' "$H" "$M"). Journal : $DIR/journal.log"
echo "Rappel : le Mac doit être allumé ou en veille (pas éteint) à cette heure ; pmset repeat wakeorpoweron peut le réveiller."
