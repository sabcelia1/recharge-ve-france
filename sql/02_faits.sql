-- =============================================================================
-- 02 — Tables de faits
-- Dialecte : Google BigQuery (Standard SQL)
-- Prérequis : 01_dimensions.sql exécuté
-- =============================================================================


-- -----------------------------------------------------------------------------
-- fct_point_recharge : 1 ligne = 1 point de recharge ouvert au public
-- Clés : code_insee -> dim_commune, date_mise_en_service -> dim_date,
--        palier_puissance -> dim_palier_puissance
-- Les points non rattachés à une commune (< 0,1 %) sont exclus.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE mart.fct_point_recharge AS
SELECT
  p.id_pdc_itinerance,
  p.id_station_itinerance,
  p.code_insee,
  p.date_mise_en_service,                  -- NULL pour environ la moitié des points
  p.puissance_nominale    AS puissance_kw,
  p.palier_puissance,
  p.implantation_station,
  p.nom_operateur,
  p.prise_type_combo_ccs  AS a_prise_ccs,
  p.gratuit               AS est_gratuit,
  p.methode_rattachement,                   -- traçabilité : INSEE / code postal / GPS
  p.longitude,
  p.latitude
FROM staging.points_recharge AS p
WHERE p.code_insee IN (SELECT code_insee FROM mart.dim_commune);


-- -----------------------------------------------------------------------------
-- fct_parc_vehicules : 1 ligne = 1 commune x 1 date d'arrêté (trimestrielle)
-- Stock de voitures particulières immatriculées (snapshot, non additif dans le temps :
-- on ne somme jamais deux trimestres entre eux).
-- Les communes absentes du référentiel actuel (fusions, < 1 %) sont exclues.
-- -----------------------------------------------------------------------------
CREATE OR REPLACE TABLE mart.fct_parc_vehicules AS
SELECT
  v.code_insee,
  v.date_arrete,
  v.nb_vp_electriques,
  v.nb_vp_total
FROM staging.vehicules AS v
WHERE v.code_insee IN (SELECT code_insee FROM mart.dim_commune);


-- -----------------------------------------------------------------------------
-- Contrôles d'intégrité référentielle (à lancer après création) :
-- chaque requête doit renvoyer 0.
-- -----------------------------------------------------------------------------
-- SELECT COUNT(*) FROM mart.fct_point_recharge f
--   LEFT JOIN mart.dim_palier_puissance d USING (palier_puissance)
--   WHERE f.palier_puissance IS NOT NULL AND d.ordre IS NULL;
--
-- SELECT COUNT(*) FROM mart.fct_point_recharge f
--   LEFT JOIN mart.dim_date d ON f.date_mise_en_service = d.date
--   WHERE f.date_mise_en_service IS NOT NULL AND d.date IS NULL;
--
-- SELECT COUNT(*) FROM (
--   SELECT id_pdc_itinerance FROM mart.fct_point_recharge
--   GROUP BY 1 HAVING COUNT(*) > 1);
