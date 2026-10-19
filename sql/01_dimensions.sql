-- =============================================================================
-- 01 — Tables de dimensions
-- Dialecte : Google BigQuery (Standard SQL)
-- Prérequis : tables brutes chargées dans le dataset `staging`
--             (communes, points_recharge, vehicules — voir docs/guide_bigquery.md)
-- =============================================================================


-- -----------------------------------------------------------------------------
-- dim_commune : 1 ligne = 1 commune (référentiel INSEE + population)
-- Porte la hiérarchie géographique commune > département > région.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE mart.dim_commune AS
SELECT
  code_insee,
  nom_commune,
  code_departement,
  nom_departement,
  code_region,
  nom_region,
  population
FROM staging.communes;


-- -----------------------------------------------------------------------------
-- dim_date : 1 ligne = 1 jour, de 2010 à la fin de l'année en cours
-- Générée en SQL (pas de fichier source) pour couvrir toutes les dates des faits.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE mart.dim_date AS
SELECT
  jour                                      AS date,
  EXTRACT(YEAR FROM jour)                   AS annee,
  EXTRACT(QUARTER FROM jour)                AS trimestre,
  CONCAT(CAST(EXTRACT(YEAR FROM jour) AS STRING), '-T',
         CAST(EXTRACT(QUARTER FROM jour) AS STRING)) AS libelle_trimestre,  -- ex. 2025-T3
  EXTRACT(MONTH FROM jour)                  AS mois,
  LAST_DAY(jour, QUARTER) = jour            AS est_fin_trimestre
FROM UNNEST(
  GENERATE_DATE_ARRAY(DATE '2010-01-01', LAST_DAY(CURRENT_DATE(), YEAR))
) AS jour;


-- -----------------------------------------------------------------------------
-- dim_palier_puissance : paliers de puissance de recharge
-- Les libellés sont identiques à ceux produits par src/clean.py (config.py).
-- "Recharge rapide" = strictement plus de 50 kW.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE mart.dim_palier_puissance AS
SELECT *
FROM UNNEST([
  STRUCT(1 AS ordre, 'Lente (≤ 7,4 kW)'        AS palier_puissance, 0.0   AS kw_min, 7.4  AS kw_max, FALSE AS est_recharge_rapide),
  STRUCT(2,          'Accélérée (7,4–22 kW)',                         7.4,             22.0,           FALSE),
  STRUCT(3,          'Rapide (22–50 kW)',                             22.0,            50.0,           FALSE),
  STRUCT(4,          'Très rapide (50–150 kW)',                       50.0,            150.0,          TRUE),
  STRUCT(5,          'Ultra-rapide (> 150 kW)',                       150.0,           NULL,           TRUE)
]);
