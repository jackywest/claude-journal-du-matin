# Mesures réelles — test du 24 octobre 2026 (macOS, Chrome, Python 3.9)

Les chiffres ci-dessous viennent d'une vraie exécution, pas d'une estimation.

## Lecture des sources (`scripts/fetch.py`)
- Sources demandées : 13 (4 versions GitHub, 7 blogs/médias/agrégateurs, 2 chaînes YouTube) ; flux lus : **13**, en erreur : **0**.
- Éléments présents dans les flux : 2 388 ; de moins de 24 h : **34** ; après dédoublonnage : **34** ; avec image : 15.
- Durée du script : **7,4 s** (3,5 s sans la recherche d'images/descriptions `og:`).
- Les 2 chaînes YouTube et plusieurs blogs n'avaient rien publié dans les dernières 24 h : 0 élément, c'est normal.
- Aucun doublon réel ce jour-là. Le dédoublonnage a donc été vérifié à part sur 4 éléments fabriqués (même histoire sous deux titres + même URL avec `utm_`) : 4 -> 2 groupes, l'un avec 2 doublons rattachés.

## Choix (fait à la main, comme le skill le demande)
34 éléments -> **8 histoires** : 1 principale + 7 en colonnes (2 / 2 / 3). Écartés (26) : 10 builds automatiques d'un dépôt de modèles, 3 versions d'un outil local, 1 version de SDK, et 12 articles ou fils sans nouveauté assez forte ou trop pointus.

## PDF (`scripts/render.sh`)
- **1 page** A4 (594,96 x 841,92 pt), vérifiée avec `pdfinfo`, puis image extraite avec `pdftoppm` et relue en entier.
- Durée du rendu : **3,4 s**. Fichiers : `une.pdf` (≈ 400 Ko), `apercu.jpg`.
- `print.sh --dry-run` : exécuté, code 0, rien imprimé. Ce Mac n'a aucune imprimante par défaut : le script l'a dit au lieu de planter. `install-6h.sh --dry-run` : plist généré et validé avec `plutil -lint` (OK), rien installé.

## Ce qui a dû être corrigé (2 passes)
Avant la passe 1 (lecture) :
1. Les vignettes des versions GitHub sont l'avatar de l'auteur, pas une photo : supprimées (le gabarit tient sans image).
2. Les images annonçaient `&#038;` dans leur URL : décodées.
3. Le gabarit des flux d'agrégateur (« Article URL: … Comments URL: … ») tenait lieu de résumé : remplacé par la description `og:description` de l'article, et les points/commentaires gardés à part.
4. Les cartes génériques GitHub (`githubassets.com`) comptées comme photos : ignorées.
5. Numéros de version et builds seuls (« v2.3.0 », « b11865 ») ajoutés au signal `mini`.

Passe 1 de mise en page : le texte de l'histoire principale était coupé (dernière ligne perdue) -> hauteur du bloc 82 -> 92 mm, corps 10,5 -> 10 pt, limite fixée à 50 mots.
Passe 2 : la colonne de gauche (3 histoires) débordait sur le pied de page -> répartition 2 / 2 / 3 écrite dans `SKILL.md`, `overflow: hidden` ajouté aux colonnes. Rendu final relu : rien de coupé.

## Limites constatées
- `SKILL.md` n'a pas été exécuté par `claude -p "/journal-du-matin"` : les étapes (lecture, choix, mise en page, PDF) ont été faites à la main en suivant ses instructions. La tâche de 6 h n'a pas été installée.
- Le résumé vient du flux : pour certains éléments (publications sur un réseau social, notes de version) il est très court, d'où des histoires prudentes.
- Le Mac doit être allumé à 6 h et chaque exécution consomme du forfait Claude.
