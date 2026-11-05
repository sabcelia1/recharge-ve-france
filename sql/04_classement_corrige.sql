-- =============================================================================
-- 04 — Classement corrigé des départements
-- Dialecte : Google BigQuery (Standard SQL)
-- Prérequis : 03_analyses.sql exécuté
--
-- Corrige les deux biais identifiés dans docs/journal_analyse.md :
--   H3 — outre-mer : couverture probablement incomplète de la base IRVE
--        -> outre-mer (codes 97x et 98x) exclu de ce classement
--   H4 — flottes d'entreprise : véhicules immatriculés au siège, pas sur place
--        -> communes avec plus de 2 voitures par habitant exclues
--           (leurs véhicules, leurs bornes et leur population)
-- =============================================================================

CREATE OR REPLACE VIEW mart.v_tension_departement_corrigee AS
WITH communes_retenues AS (
  SELECT *
  FROM mart.v_tension_commune
  -- Métropole uniquement : exclut les DROM (971 à 976) et les collectivités
  -- d'outre-mer (975, 977, 978, 986 à 988, ex. Nouvelle-Calédonie = 988)
  WHERE NOT (STARTS_WITH(code_departement, '97') OR STARTS_WITH(code_departement, '98'))
),
departements AS (
  SELECT
    code_departement,
    ANY_VALUE(nom_departement)                                    AS nom_departement,
    ANY_VALUE(nom_region)                                         AS nom_region,
    COUNTIF(COALESCE(suspicion_flotte, FALSE))                    AS nb_communes_exclues,
    SUM(IF(COALESCE(suspicion_flotte, FALSE), nb_ve, 0))          AS nb_ve_exclus,
    SUM(IF(COALESCE(suspicion_flotte, FALSE), 0, population))     AS population,
    SUM(IF(COALESCE(suspicion_flotte, FALSE), 0, nb_ve))          AS nb_ve,
    SUM(IF(COALESCE(suspicion_flotte, FALSE), 0, nb_points))      AS nb_points,
    SUM(IF(COALESCE(suspicion_flotte, FALSE), 0, nb_points_rapides)) AS nb_points_rapides
  FROM communes_retenues
  GROUP BY code_departement
)
SELECT
  code_departement,
  nom_departement,
  nom_region,
  nb_communes_exclues,
  nb_ve_exclus,
  population,
  nb_ve,
  nb_points,
  nb_points_rapides,
  SAFE_DIVIDE(nb_ve, nb_points)                       AS ve_par_point,
  SAFE_DIVIDE(nb_points, population) * 10000          AS points_pour_10k_hab,
  SAFE_DIVIDE(nb_points_rapides, nb_points)           AS part_points_rapides,
  RANK() OVER (ORDER BY SAFE_DIVIDE(nb_ve, nb_points) DESC) AS rang_tension
FROM departements;
