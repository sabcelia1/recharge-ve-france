# Power BI

## Rapport

`recharge-ve-france.pbip` est le rapport au format **Projet Power BI**, lisible dans Git :

- `recharge-ve-france.SemanticModel/definition/` : le modèle en TMDL (tables, relations dans `relationships.tmdl`, mesures DAX dans `tables/fct_point_recharge.tmdl`) ;
- `recharge-ve-france.Report/definition/` : les 5 pages et leurs visuels.

Les données ne sont pas versionnées (`cache.abf` exclu). Pour ouvrir le rapport :

1. Construire les tables dans BigQuery (voir [`docs/guide_bigquery.md`](../docs/guide_bigquery.md), scripts `sql/01` à `sql/05`).
2. Ouvrir `recharge-ve-france.pbip` dans Power BI Desktop.
3. Remplacer le projet Google Cloud `recharge-ve-france` par le vôtre si besoin (*Transformer les données → Paramètres de la source de données*), puis **Actualiser**.

- `theme_recharge_ve.json` : thème du rapport (couleurs, polices, cartes, tableaux). À importer dans Power BI Desktop via **Afficher → Thèmes → Parcourir les thèmes**.
- Palette : bleu nuit `#14213D` (structure), vert électrique `#0E9F8E` (donnée principale), ambre `#F2A541` (mise en évidence), gris `#5B6676` (texte secondaire), fond `#EEF2F6`.

## Icônes

Dossier `icones/` : 6 pictogrammes dessinés pour le rapport (`voiture`, `borne`, `habitants`, `region`, `eclair`, `ratio`), en trois couleurs (`vert`, `bleu`, `blanc`), aux formats PNG (256 px) et SVG. Aperçu : `icones/apercu.png`.

## Fonds de page

Dossier `fonds/` : un fond par page (`png/`, 2560×1440 pour une page Power BI 1280×720), avec le bandeau, les titres, les messages clés et les panneaux sur lesquels se posent les visuels.

- Générés par `fonds/generer_fonds.py` (HTML) puis `fonds/capture.js` (PNG via Playwright).
- À utiliser avec `theme_recharge_ve_fonds.json` : visuels sans fond, bordure, ombre ni titre (les titres sont dessinés sur le fond).
- Position et taille de chaque visuel : `fonds/positions.json` (x, y, largeur, hauteur en pixels).
- Mise en place : *Format de la page → Arrière-plan du canevas → Image → Parcourir*, ajustement **Ajuster**, transparence **0 %**.
