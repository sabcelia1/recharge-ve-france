-- =============================================================================
-- 03 — Vues d'analyse (couche consommée par Power BI et Looker Studio)
-- Dialecte : Google BigQuery (Standard SQL)
-- Prérequis : 01_dimensions.sql et 02_faits.sql exécutés
-- =============================================================================


-- -----------------------------------------------------------------------------
-- v_tension_departement : indicateurs clés par département
-- Photo à date : parc VE du dernier trimestre disponible vs points en service.
-- Ratio de tension = véhicules électriques par point de recharge public.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW mart.v_tension_departement AS
WITH dernier_trimestre AS (
  SELECT MAX(date_arrete) AS date_arrete
  FROM mart.fct_parc_vehicules
),
parc AS (
  SELECT
    c.code_departement,
    SUM(v.nb_vp_electriques) AS nb_ve,
    SUM(v.nb_vp_total)       AS nb_vp
  FROM mart.fct_parc_vehicules AS v
  JOIN dernier_trimestre       USING (date_arrete)
  JOIN mart.dim_commune AS c   USING (code_insee)
  GROUP BY c.code_departement
),
points AS (
  SELECT
    c.code_departement,
    COUNT(*)                                         AS nb_points,
    COUNTIF(pa.est_recharge_rapide)                  AS nb_points_rapides,
    COUNT(DISTINCT p.id_station_itinerance)          AS nb_stations
  FROM mart.fct_point_recharge AS p
  JOIN mart.dim_commune AS c               USING (code_insee)
  LEFT JOIN mart.dim_palier_puissance AS pa USING (palier_puissance)
  GROUP BY c.code_departement
),
departements AS (
  SELECT
    code_departement,
    ANY_VALUE(nom_departement) AS nom_departement,
    ANY_VALUE(nom_region)      AS nom_region,
    SUM(population)            AS population
  FROM mart.dim_commune
  GROUP BY code_departement
)
SELECT
  d.code_departement,
  d.nom_departement,
  d.nom_region,
  d.population,
  (SELECT date_arrete FROM dernier_trimestre)               AS date_parc,
  pa.nb_ve,
  pa.nb_vp,
  SAFE_DIVIDE(pa.nb_ve, pa.nb_vp)                           AS part_ve_dans_parc,
  pt.nb_stations,
  pt.nb_points,
  pt.nb_points_rapides,
  SAFE_DIVIDE(pa.nb_ve, pt.nb_points)                       AS ve_par_point,
  SAFE_DIVIDE(pt.nb_points, d.population) * 10000           AS points_pour_10k_hab,
  SAFE_DIVIDE(pt.nb_points_rapides, pt.nb_points)           AS part_points_rapides,
  RANK() OVER (ORDER BY SAFE_DIVIDE(pa.nb_ve, pt.nb_points) DESC) AS rang_tension
FROM departements AS d
LEFT JOIN parc   AS pa USING (code_departement)
LEFT JOIN points AS pt USING (code_departement);


-- -----------------------------------------------------------------------------
-- v_tension_commune : mêmes indicateurs à la maille commune (zoom du dashboard)
-- ⚠️ Biais flottes d'entreprise : un véhicule est rattaché à l'adresse de son
-- titulaire (siège social, loueur). À interpréter avec prudence.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW mart.v_tension_commune AS
WITH dernier_trimestre AS (
  SELECT MAX(date_arrete) AS date_arrete FROM mart.fct_parc_vehicules
),
parc AS (
  SELECT v.code_insee, v.nb_vp_electriques AS nb_ve, v.nb_vp_total AS nb_vp
  FROM mart.fct_parc_vehicules AS v
  JOIN dernier_trimestre USING (date_arrete)
),
points AS (
  SELECT
    p.code_insee,
    COUNT(*)                        AS nb_points,
    COUNTIF(pa.est_recharge_rapide) AS nb_points_rapides
  FROM mart.fct_point_recharge AS p
  LEFT JOIN mart.dim_palier_puissance AS pa USING (palier_puissance)
  GROUP BY p.code_insee
)
SELECT
  c.code_insee,
  c.nom_commune,
  c.code_departement,
  c.nom_departement,
  c.nom_region,
  c.population,
  COALESCE(pa.nb_ve, 0)                                     AS nb_ve,
  pa.nb_vp,
  COALESCE(pt.nb_points, 0)                                 AS nb_points,
  COALESCE(pt.nb_points_rapides, 0)                         AS nb_points_rapides,
  SAFE_DIVIDE(pa.nb_ve, pt.nb_points)                       AS ve_par_point,
  SAFE_DIVIDE(pt.nb_points, c.population) * 10000           AS points_pour_10k_hab,
  -- Signal des communes probablement gonflées par des flottes
  SAFE_DIVIDE(pa.nb_vp, c.population) > 2                   AS suspicion_flotte
FROM mart.dim_commune AS c
LEFT JOIN parc   AS pa USING (code_insee)
LEFT JOIN points AS pt USING (code_insee);


-- -----------------------------------------------------------------------------
-- v_evolution_trimestrielle : dynamique nationale, trimestre par trimestre
-- Points en service à chaque trimestre = points dont la date de mise en service
-- est connue et antérieure à la date d'arrêté. Environ la moitié des points n'ont
-- pas de date : cette courbe sous-estime le niveau, mais montre la tendance.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW mart.v_evolution_trimestrielle AS
WITH parc AS (
  SELECT
    date_arrete,
    SUM(nb_vp_electriques) AS nb_ve,
    SUM(nb_vp_total)       AS nb_vp
  FROM mart.fct_parc_vehicules
  GROUP BY date_arrete
),
mises_en_service AS (
  SELECT date_mise_en_service, COUNT(*) AS nb
  FROM mart.fct_point_recharge
  WHERE date_mise_en_service IS NOT NULL
  GROUP BY date_mise_en_service
)
SELECT
  p.date_arrete,
  d.libelle_trimestre,
  p.nb_ve,
  p.nb_vp,
  SAFE_DIVIDE(p.nb_ve, p.nb_vp)                             AS part_ve_dans_parc,
  SUM(IF(m.date_mise_en_service <= p.date_arrete, m.nb, 0)) AS nb_points_date_connue,
  SAFE_DIVIDE(p.nb_ve,
    SUM(IF(m.date_mise_en_service <= p.date_arrete, m.nb, 0))) AS ve_par_point_date_connue
FROM parc AS p
LEFT JOIN mart.dim_date AS d ON d.date = p.date_arrete
CROSS JOIN mises_en_service AS m
GROUP BY p.date_arrete, d.libelle_trimestre, p.nb_ve, p.nb_vp;
