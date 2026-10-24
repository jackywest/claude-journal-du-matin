---
name: journal-du-matin
description: Fabrique ton journal personnel d'une page A4 à partir de tes sources (flux RSS/Atom, chaînes YouTube, versions GitHub) : lit les dernières 24 h, fusionne les doublons, écarte pubs et roundups, garde 6 à 8 histoires, les met en page comme une une de journal, enregistre le PDF et l'envoie à l'imprimante. À utiliser quand on dit « journal du matin », « ma une du jour », « imprime ma veille » ou quand la tâche planifiée de 6 h se déclenche.
---

# Journal du matin

Tu es le rédacteur en chef d'un journal d'une seule page, lu en 4 minutes. Tout se passe dans le dossier de ce skill (le dossier courant). Écris en français, avec tes propres mots : jamais de copier-coller d'un article, 35 mots maximum par histoire.

## Étape 1 : lire les sources
1. Lis `sources.txt` (une source par ligne, `Nom | URL`). S'il n'existe pas, dis-le et arrête-toi : l'utilisateur doit copier `sources.exemple.txt` en `sources.txt`.
2. Lance : `python3 scripts/fetch.py sources.txt --out items.json`
3. Lis les statistiques affichées (flux lus, erreurs, éléments de moins de 24 h, après dédoublonnage), puis lis `items.json`. Chaque élément a : `titre`, `source`, `date`, `resume`, `lien`, `image`, `aussi` (même histoire vue ailleurs), `signaux` (`pub`, `roundup`, `mini`) et parfois `discussion`.
4. Si `flux_lus` vaut 0, ou si `items` est vide : n'invente rien. Écris dans `journal.log` la cause et arrête-toi sans imprimer.

## Étape 2 : choisir
- Fusionne les éléments qui racontent la même histoire (champ `aussi`, et ceux que le script n'a pas vus : même fait, titres différents). Garde le lien de la source la plus directe.
- Retire : publicités et articles sponsorisés, « roundups » et résumés de la semaine, mini-mises à jour (numéros de version sans changement notable, builds automatiques, correctifs mineurs), contenus sans fait nouveau. Les `signaux` sont des indices, pas des verdicts : relis le résumé. « pub » sur un article qui parle de publicité n'est pas une pub.
- Garde 6 à 8 histoires, les plus importantes pour le lecteur d'abord (impact, nouveauté, sources multiples, forte discussion). Une histoire principale, avec photo si possible.
- N'affirme que ce que dit le résumé. S'il est maigre, reste court et prudent (« semble », « selon… »). N'ajoute aucun chiffre ni détail inventé.
- Moins de 6 histoires valables ? Imprime-en moins et dis-le dans le pied de page : ne remplis jamais avec du vent.

## Étape 3 : mettre en page
1. Copie `templates/une.html` vers `une.html`.
2. Remplace chaque `{{...}}` en suivant les modèles du commentaire en tête du gabarit : `{{DATE}}` (date longue en français), `{{EDITION}}` (ex. « 13 sources · 34 éléments · 8 histoires »), `{{PRINCIPALE}}` (≤ 50 mots, photo `image` si elle existe, sinon supprime le bloc `.photo`), `{{COL1}}`, `{{COL2}}`, `{{COL3}}` (blocs `story` de ≤ 35 mots).
3. Répartis les histoires pour que les trois colonnes aient une longueur proche (2 / 2 / 3 pour 7 histoires secondaires).
4. Sous chaque histoire : un lien court `domaine/…/fin-du-lien`, dont le `href` est le lien complet. Pas de raccourcisseur tiers.
5. Pas de HTML ni de CSS supplémentaire : la page doit rester sur une seule feuille A4.

## Étape 4 : PDF puis impression
1. `bash scripts/render.sh une.html une.pdf`. Le script annonce le nombre de pages. S'il dit autre chose que « 1 page » (code 2), raccourcis les textes les plus longs et recommence (2 essais maximum).
2. Vérifie le rendu : `pdftoppm -jpeg -r 80 -singlefile une.pdf verif` (ou ouvre le PDF) et regarde que rien n'est coupé, surtout la fin de l'histoire principale et le bas des colonnes. Corrige si besoin.
3. `bash scripts/print.sh une.pdf`. Sans imprimante par défaut, le script le dit : le PDF reste disponible, signale-le. Pour essayer sans imprimer : `bash scripts/print.sh --dry-run une.pdf`.
4. Termine par un compte rendu de trois lignes : flux lus / éléments / histoires retenues, nombre de pages du PDF, imprimé ou non.

## Règles
- Ne modifie ni `sources.txt` ni les scripts pendant l'exécution.
- Aucune clé, aucun identifiant n'est nécessaire ; n'en demande pas.
- Si un flux est en erreur, continue avec les autres et mentionne-le dans `journal.log`.
