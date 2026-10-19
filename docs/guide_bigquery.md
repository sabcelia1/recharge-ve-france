# Guide : charger les données dans BigQuery (gratuit, sans carte bancaire)

Tout se fait dans le navigateur, dans la console BigQuery. Durée : environ 20 minutes.

> **BigQuery Sandbox** : gratuit, mais les tables expirent automatiquement après 60 jours.
> Ce n'est pas un problème : tout se recrée en relançant les étapes 3 et 4.

## 1. Ouvrir BigQuery et créer un projet

1. Allez sur <https://console.cloud.google.com/bigquery> avec votre compte Google.
2. Acceptez les conditions si c'est votre première visite.
3. Créez un projet (en haut à gauche, sélecteur de projet → **Nouveau projet**), par exemple `recharge-ve-france`. Aucune facturation n'est demandée en mode Sandbox.

## 2. Créer les deux datasets

Dans le panneau **Explorer** à gauche, cliquez sur les **⋮** à côté du nom du projet → **Créer un ensemble de données** :

| Nom (ID) | Rôle | Emplacement |
|---|---|---|
| `staging` | Données nettoyées importées depuis Python | `EU` (multirégion) |
| `mart` | Modèle en étoile et vues d'analyse | `EU` (multirégion) |

⚠️ Les deux datasets doivent avoir **le même emplacement** (`EU`), sinon les requêtes échouent.

## 3. Importer les 3 fichiers Parquet dans `staging`

Les fichiers sont produits par `lancer.bat` dans `data/processed/`.

Pour chacun des 3 fichiers, **⋮** à côté de `staging` → **Créer une table** :

| Champ | Valeur |
|---|---|
| Créer une table à partir de | **Importer** |
| Sélectionner un fichier | `data/processed/communes.parquet` |
| Format de fichier | **Parquet** |
| Table | `communes` |

Puis **Créer la table**. Recommencez avec :
- `points_recharge.parquet` → table `points_recharge`
- `vehicules.parquet` → table `vehicules`

Le schéma (types des colonnes) est détecté automatiquement depuis le Parquet.

## 4. Construire le modèle en étoile

Cliquez sur **+** (nouvel onglet de requête). Pour chaque fichier du dossier `sql/`, **dans l'ordre** :

1. Ouvrez le fichier avec le Bloc-notes, copiez tout son contenu.
2. Collez-le dans l'éditeur BigQuery.
3. Cliquez sur **Exécuter**.

| Ordre | Fichier | Crée |
|---|---|---|
| 1 | `sql/01_dimensions.sql` | `dim_commune`, `dim_date`, `dim_palier_puissance` |
| 2 | `sql/02_faits.sql` | `fct_point_recharge`, `fct_parc_vehicules` |
| 3 | `sql/03_analyses.sql` | `v_tension_departement`, `v_tension_commune`, `v_evolution_trimestrielle` |

## 5. Vérifier

Collez et exécutez :

```sql
SELECT nom_departement, nb_ve, nb_points, ROUND(ve_par_point, 1) AS ve_par_point, rang_tension
FROM mart.v_tension_departement
ORDER BY rang_tension
LIMIT 10;
```

Vous obtenez les 10 départements où il y a le plus de véhicules électriques par point de recharge.
