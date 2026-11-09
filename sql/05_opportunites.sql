-- =============================================================================
-- 05 — Opportunités d'implantation de bornes
-- Dialecte : Google BigQuery (Standard SQL)
-- Prérequis : 03_analyses.sql exécuté
--
-- Question : où installer des points de recharge publics en priorité ?
-- Périmètre : communes de plus de 30 000 habitants, métropole, hors communes
--             à suspicion de flotte (mêmes règles que la page « déserts »).
--
-- Deux repères calculés sur ce périmètre (médianes, pour ne pas être tirées
-- par les extrêmes comme Puteaux ou Vitry-sur-Seine) :
--   densite_mediane : points de recharge pour 10 000 habitants
--   tension_mediane : véhicules électriques par point
--
-- Profils :
--   1 · Demande non servie : moins équipée que la médiane ET plus de VE par point
--                            que la médiane -> la demande existe déjà
--   2 · Rattrapage         : moins de la moitié de la densité médiane, mais peu
--                            de VE pour l'instant -> pari sur l'adoption future
--   3 · Sans urgence       : le reste (densité correcte, ou déficit avec peu de demande)
--
-- points_manquants : nombre de points à installer pour atteindre la densité
--                    médiane (estimation de la taille du marché, pas un objectif)
-- =============================================================================

CREATE OR REPLACE VIEW mart.v_opportunites_commune AS
WITH perimetre AS (
  SELECT *
  FROM mart.v_tension_commune
  WHERE population >= 30000
    AND NOT (STARTS_WITH(code_departement, '97') OR STARTS_WITH(code_departement, '98'))
    AND NOT COALESCE(suspicion_flotte, FALSE)
),
reperes AS (
  SELECT
    APPROX_QUANTILES(points_pour_10k_hab, 2)[OFFSET(1)] AS densite_mediane,
    APPROX_QUANTILES(ve_par_point, 2)[OFFSET(1)]        AS tension_mediane
  FROM perimetre
)
SELECT
  p.code_insee,
  p.nom_commune,
  p.code_departement,
  p.nom_departement,
  p.nom_region,
  p.population,
  p.nb_ve,
  p.nb_points,
  p.nb_points_rapides,
  p.points_pour_10k_hab,
  p.ve_par_point,
  p.part_ve_dans_parc,
  r.densite_mediane,
  r.tension_mediane,
  GREATEST(0, CAST(ROUND(r.densite_mediane * p.population / 10000 - p.nb_points) AS INT64))
                                                                   AS points_manquants,
  CASE
    WHEN p.points_pour_10k_hab < r.densite_mediane
     AND p.ve_par_point > r.tension_mediane          THEN '1 · Demande non servie'
    WHEN p.points_pour_10k_hab < r.densite_mediane / 2 THEN '2 · Rattrapage'
    ELSE '3 · Sans urgence'
  END                                                              AS profil
FROM perimetre AS p
CROSS JOIN reperes AS r;
