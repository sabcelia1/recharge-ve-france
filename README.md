# ⚡ Recharge électrique en France : où les bornes manquent-elles ?

> Analyse de l'adéquation entre le parc de voitures électriques et l'infrastructure de recharge publique, à l'échelle des communes et des départements français.

**Statut :** 🚧 en cours — semaine 1/4 (ingestion et nettoyage)

---

## 🎯 Problématique

Le parc de voitures électriques progresse rapidement en France. Les points de recharge publics suivent-ils le rythme partout ?

Ce projet identifie les **territoires sous-équipés**, où le nombre de véhicules électriques par point de recharge est le plus élevé, et suit l'évolution de cet écart dans le temps.

## 📊 Indicateurs clés

| Indicateur | Définition |
|---|---|
| Ratio de tension | Véhicules électriques / points de recharge publics |
| Densité de recharge | Points de recharge pour 10 000 habitants |
| Part de recharge rapide | Points > 50 kW / total des points |
| Dynamique | Croissance annuelle du parc électrique vs des points de recharge |

## 🏗️ Architecture

```
 Open data (data.gouv.fr, geo.api.gouv.fr)
        │
        ▼
 [1] src/ingest.py   ── téléchargement + manifeste de provenance ──►  data/raw/
        │
        ▼
 [2] src/clean.py    ── nettoyage + contrôles qualité ──►  data/processed/*.parquet
        │                                                   reports/qualite_donnees.md
        ▼
 [3] BigQuery        ── modèle en étoile (SQL)                       (semaine 2)
        │
        ▼
 [4] Power BI + Looker Studio  ── dashboards                         (semaine 3)
```

## 📁 Sources de données

| Source | Producteur | Granularité | Licence |
|---|---|---|---|
| [Base nationale consolidée IRVE (données statiques)](https://www.data.gouv.fr/datasets/beta-bases-nationales-des-points-de-recharge-pour-vehicules-electriques-en-france-irve) | Point d'Accès National transport.data.gouv.fr | Point de recharge | Licence Ouverte 2.0 |
| [Voitures particulières immatriculées par commune et par type de recharge](https://www.data.gouv.fr/datasets/voitures-particulieres-immatriculees-par-commune-et-par-type-de-recharge-jeu-de-donnees-aaadata) | Agence ORE / AAA Data | Commune × trimestre | Licence Ouverte 2.0 |
| [API Découpage administratif](https://geo.api.gouv.fr/decoupage-administratif) | Etalab | Commune (+ population) | Licence Ouverte 2.0 |

## 🧹 Qualité des données

Le nettoyage applique des règles explicites, chacune tracée dans [`reports/qualite_donnees.md`](reports/qualite_donnees.md) :

- **Doublons** : suppression sur l'identifiant unique du point de recharge (`id_pdc_itinerance`).
- **Unités** : puissances saisies en watts au lieu de kilowatts détectées et converties.
- **Valeurs aberrantes** : puissances hors [1 ; 1000] kW et dates de mise en service incohérentes (avant 2010 ou dans le futur) mises à vide plutôt que supprimées.
- **Rattachement aux communes** : environ un quart des points de recharge n'ont pas de code INSEE exploitable. Ils sont rattachés par ordre de fiabilité : code INSEE déclaré, puis code postal saisi à la place du code INSEE, puis **coordonnées GPS** (commune dont le centre est le plus proche, à moins de 15 km). Chaque point garde la méthode utilisée dans `methode_rattachement`.
- **Codes INSEE** : normalisation sur 5 caractères (Corse `2A`/`2B` comprise), arrondissements de Paris, Lyon et Marseille ramenés à leur commune pour que les sources se joignent correctement.
- **Cohérence** : exclusion des lignes où le nombre de véhicules électriques dépasse le parc total.
- **Traçabilité** : un manifeste (`data/raw/manifest.json`) date chaque téléchargement.

## ⚠️ Limites connues

- Le rattachement par coordonnées GPS utilise le centre de la commune la plus proche : près d'une limite communale, un point peut être attribué à la commune voisine. L'effet est négligeable à la maille départementale.
- Les véhicules sont rattachés à l'**adresse d'immatriculation**. Les flottes d'entreprise et de loueurs gonflent artificiellement certaines communes (sièges sociaux, zones aéroportuaires). L'analyse au niveau **départemental** atténue ce biais.
- La base IRVE ne couvre que la **recharge ouverte au public**, pas la recharge à domicile ou en entreprise.
- La base IRVE consolidée est en version **bêta** et dépend des déclarations des aménageurs.

## 🚀 Reproduire le projet

**Windows :** double-cliquez sur `lancer.bat` (crée l'environnement, télécharge et nettoie les données).

**Manuellement :**

```bash
git clone https://github.com/sabcelia1/recharge-ve-france.git
cd recharge-ve-france
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\Scripts\activate
pip install -r requirements.txt

python src/ingest.py               # ~180 Mo de téléchargement
python src/clean.py                # tables propres + rapport qualité
jupyter notebook notebooks/01_exploration.ipynb
```

## 🗺️ Feuille de route

- [x] **Semaine 1** — Ingestion, nettoyage, rapport qualité, exploration
- [ ] **Semaine 2** — Chargement BigQuery, modèle en étoile, requêtes SQL
- [ ] **Semaine 3** — Dashboard Power BI (.pbip) et version Looker Studio
- [ ] **Semaine 4** — Conclusions, captures, publication

## 🛠️ Stack

Python (pandas, requests) · SQL · Google BigQuery · Power BI (DAX, Power Query) · Looker Studio

---

👤 **Célia Monga** — Ingénieure Data & IA · [LinkedIn](https://www.linkedin.com/in/c%C3%A9lia-monga-a48b48242/)
