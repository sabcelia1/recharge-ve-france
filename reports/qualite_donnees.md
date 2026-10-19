# Rapport de qualité des données

_Généré par `src/clean.py` sur les données téléchargées en octobre 2026. Relancer `lancer.bat` pour le régénérer sur les données du jour._

| Table | Contrôle | Résultat |
|---|---|---|
| communes | lignes | 34,969 |
| communes | population manquante | 6 |
| irve | lignes brutes | 170,624 |
| irve | doublons id_pdc_itinerance supprimés | 2 |
| irve | puissances saisies en W (converties en kW) | 19 |
| irve | puissances manquantes ou aberrantes (mises à vide) | 2750 |
| irve | dates manquantes ou illisibles | 82848 |
| irve | dates incohérentes (avant 2010 ou futures, mises à vide) | 6 |
| irve | code commune déclaré vide | 44,606 |
| irve | codes non reconnus les plus fréquents | '86000' (106), '99999' (104), '33700' (36), '75014' (36), '13590' (34) |
| irve | rattachement commune — code INSEE | 124,025 (72.7%) |
| irve | rattachement commune — coordonnées GPS | 44,973 (26.4%) |
| irve | rattachement commune — code postal corrigé | 1,552 (0.9%) |
| irve | rattachement commune — non rattaché | 72 (0.0%) |
| vehicules | encodage détecté | cp1252 |
| vehicules | lignes brutes | 773,782 |
| vehicules | lignes où VE > total (incohérentes, exclues) | 0 |
| vehicules | trimestres couverts | 2020-12 → 2026-08 (22 trimestres) |
| vehicules | codes INSEE absents du référentiel communes | 5,794 (0.7%) |
