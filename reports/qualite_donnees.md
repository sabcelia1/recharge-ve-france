# Rapport de qualité des données

_Généré automatiquement par `src/clean.py` le 28/10/2026. Ce sont les données chargées dans BigQuery et utilisées pour toutes les analyses._

| Table | Contrôle | Résultat |
|---|---|---|
| communes | lignes | 34,969 |
| communes | population manquante | 6 |
| irve | lignes brutes | 177,956 |
| irve | doublons id_pdc_itinerance supprimés | 2 |
| irve | puissances saisies en W (converties en kW) | 17 |
| irve | puissances manquantes ou aberrantes (mises à vide) | 2704 |
| irve | dates manquantes ou illisibles | 83674 |
| irve | dates incohérentes (avant 2010 ou futures, mises à vide) | 6 |
| irve | code commune déclaré vide | 50,267 |
| irve | codes non reconnus les plus fréquents | '86000' (106), '99999' (94), '33000' (70), '13590' (34), '13290' (32) |
| irve | rattachement commune — code INSEE | 125,824 (70.7%) |
| irve | rattachement commune — coordonnées GPS | 50,622 (28.4%) |
| irve | rattachement commune — code postal corrigé | 1,432 (0.8%) |
| irve | rattachement commune — non rattaché | 76 (0.0%) |
| vehicules | encodage détecté | cp1252 |
| vehicules | lignes brutes | 773,782 |
| vehicules | lignes où VE > total (incohérentes, exclues) | 0 |
| vehicules | trimestres couverts | 2020-12 → 2026-08 (22 trimestres) |
| vehicules | codes INSEE absents du référentiel communes | 5,794 (0.7%) |
