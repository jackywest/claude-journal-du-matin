# Journal du matin

Un skill Claude Code qui imprime, chaque matin, **ta propre une de journal d'une page** : tu listes tes sources une fois, Claude lit les dernières 24 h pendant que tu dors, garde 6 à 8 histoires, met en page, enregistre le PDF et l'envoie à l'imprimante. Elle t'attend à côté du café ; tu es à jour en environ 4 minutes.

![aperçu](exemple/apercu.jpg)

## Installation en 3 étapes

1. **Installer le skill** (Claude Code et Python 3 requis ; Chrome pour le PDF, sur macOS) :
   ```bash
   git clone https://github.com/jackywest/claude-journal-du-matin.git
   cd claude-journal-du-matin
   ln -s "$PWD" ~/.claude/skills/journal-du-matin
   ```
2. **Lister tes sources** dans `sources.txt` (copie `sources.exemple.txt`) : une ligne `Nom | URL`.
   - blog ou newsletter : l'adresse de son flux RSS ou Atom ;
   - chaîne YouTube : `https://www.youtube.com/feeds/videos.xml?channel_id=…` ;
   - dépôt GitHub : `https://github.com/<owner>/<repo>/releases.atom`.
3. **Programmer 6 h** : `bash scripts/install-6h.sh --dry-run` pour voir la tâche launchd, puis `bash scripts/install-6h.sh` pour l'installer (`--uninstall` pour la retirer). Définis aussi une imprimante par défaut.

Pour essayer tout de suite, sans imprimer : dans ce dossier, lance `claude -p "/journal-du-matin"` puis `bash scripts/print.sh --dry-run une.pdf`.

## Ce que contient le dépôt
| Fichier | Rôle |
|---|---|
| `SKILL.md` | les instructions données à Claude |
| `scripts/fetch.py` | lit les flux (Python 3 standard), garde < 24 h, dédoublonne, sort un JSON |
| `templates/une.html` | gabarit A4 : bandeau + date, histoire principale + photo, 3 colonnes, lien sous chaque histoire |
| `scripts/render.sh` | HTML → PDF avec Chrome en ligne de commande, vérifie « 1 page » |
| `scripts/print.sh` | `lp` vers l'imprimante par défaut ; `--dry-run` n'imprime rien |
| `scripts/install-6h.sh` | tâche launchd à 6 h ; `--dry-run` affiche seulement le plist |
| `exemple/` | une page réelle (PDF + JPEG) et les mesures du test |

## Limites (à lire)
- **Mac et imprimante allumés** (ou en veille) à 6 h. Un Mac éteint n'exécute rien ; `sudo pmset repeat wakeorpoweron MTWRFSU 05:55:00` peut le réveiller. Une imprimante éteinte ou sans papier garde la tâche en attente ou la perd.
- **Chaque exécution consomme un peu de ton forfait Claude** (lecture du JSON, rédaction, vérification).
- Le tri et la fusion sont faits par Claude : ils peuvent se tromper. Le résumé vient du flux, pas de l'article entier ; certains flux n'en donnent presque pas.
- Seuls les éléments publiés dans les 24 dernières heures comptent : les matins calmes donnent moins de 6 histoires, et c'est volontaire.
- Les chaînes YouTube peuvent n'avoir rien publié ; les versions GitHub très fréquentes (builds automatiques) sont écartées comme mini-mises à jour.
- Le « lien court » est une version abrégée de l'adresse, pas un raccourcisseur.
- Testé sur macOS avec Chrome ; `launchd` et `lp` sont propres à macOS (le reste fonctionne ailleurs avec `CHROME=/chemin/vers/chrome`).

## Licence
MIT © Jacky West
