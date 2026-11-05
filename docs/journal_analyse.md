# Journal d'analyse

Ce journal trace la démarche suivie : ce qui a été observé, les hypothèses formulées, la façon dont elles ont été testées et les décisions qui en découlent. Il est tenu au fil du projet, y compris pour les pistes qui se sont révélées fausses.

**Légende des statuts :** ✅ validée · ❌ rejetée · 🔍 à vérifier · 📌 décision

---

## Synthèse des hypothèses

| # | Hypothèse | Statut |
|---|---|---|
| H1 | Les bornes non rattachées à une commune ont un code postal saisi à la place du code INSEE | ❌ rejetée (0,9 % seulement) |
| H2 | Ces bornes ont un code commune vide, mais des coordonnées GPS exploitables | ✅ validée (26,4 % récupérés) |
| H3 | Le classement de l'outre-mer reflète une sous-déclaration des bornes, pas un réel sous-équipement | 🔍 à vérifier |
| H4 | Les départements d'Île-de-France sont gonflés par les flottes d'entreprise et de loueurs | ✅ partiellement validée (Yvelines, Seine-Saint-Denis) |
| H5 | Les départements ruraux du classement (Aisne, Haute-Loire, Haute-Corse) sont de vrais territoires sous-équipés | 🔍 à vérifier |
| H6 | La tension résiduelle des Hauts-de-Seine vient de flottes non détectées par le seuil de 2 voitures par habitant | 🔍 à vérifier |

---

## Semaine 1 — Qualité des données

### Constat : 27 % des points de recharge non rattachés à une commune

Au premier passage du nettoyage, 46 597 points sur 170 624 (27,3 %) avaient un code commune absent du référentiel INSEE. Sans rattachement, ces points disparaissent de toute analyse géographique : le problème est bloquant.

### H1 — Codes postaux saisis à la place des codes INSEE ❌

- **Raisonnement :** confusion fréquente dans les données déclaratives françaises (ex. `75014` code postal vs `75056` code INSEE de Paris).
- **Test :** conversion des codes non reconnus via la table de correspondance code postal → code INSEE du référentiel des communes.
- **Résultat :** seuls **1 552 points (0,9 %)** corrigés. Le taux de non-rattachés restait à 26,4 %.
- **Conclusion :** hypothèse rejetée comme cause principale, mais la correction est conservée (elle reste juste pour ces 1 552 points).

### H2 — Codes vides, mais coordonnées GPS présentes ✅

- **Test :** ajout d'un diagnostic dans `clean.py` affichant le nombre de codes vides et les codes non reconnus les plus fréquents.
- **Observation :** **44 606 points ont un code commune vide**. Parmi les codes non vides non reconnus, on trouve des valeurs factices comme `99999` (104 points).
- **Solution :** rattachement à la commune dont le centre est le plus proche des coordonnées GPS (distance maximale 15 km, calcul sur la sphère pour rester exact en outre-mer).
- **Résultat :** **44 973 points récupérés (26,4 %)**. Il reste **72 points non rattachés (< 0,1 %)**.
- **Limite acceptée :** près d'une limite communale, un point peut être attribué à la commune voisine. Effet négligeable à la maille départementale, qui est la maille principale de l'analyse.
- **Traçabilité :** la colonne `methode_rattachement` indique pour chaque point la méthode utilisée (code INSEE, code postal, coordonnées GPS).

### 📌 Dates de mise en service manquantes (49 %)

- **Constat :** 82 848 points sur 170 624 n'ont pas de date de mise en service exploitable.
- **Options envisagées :** (a) supprimer ces points, (b) imputer une date, (c) les conserver avec une date vide.
- **Décision :** option (c). Supprimer fausserait tous les comptages actuels ; imputer inventerait de l'information.
- **Conséquence :** les indicateurs « photo à date » utilisent tous les points. La courbe d'évolution dans le temps n'utilise que les points datés : elle **sous-estime le niveau** mais reste exploitable pour la **tendance**, ce qui est signalé dans la vue `v_evolution_trimestrielle`.

### Autres constats

| Constat | Traitement |
|---|---|
| Fichier véhicules encodé en Windows-1252 et non en UTF-8 | Détection automatique de l'encodage |
| 19 puissances saisies en watts au lieu de kilowatts | Conversion automatique (valeurs > 1 000) |
| 2 750 puissances manquantes ou aberrantes | Mises à vide, points conservés |
| 5 794 lignes véhicules (0,7 %) avec un code commune absent du référentiel actuel | Probablement des communes fusionnées depuis ; exclues du modèle |

Détail chiffré : [`reports/qualite_donnees.md`](../reports/qualite_donnees.md).

---

## Semaine 2 — Premier classement des départements

### Résultat brut

Requête sur `mart.v_tension_departement`, dernier trimestre disponible du parc de véhicules :

| Rang | Département | Véhicules électriques | Points de recharge | VE par point |
|---|---|---:|---:|---:|
| 1 | Martinique | 6 397 | 36 | 177,7 |
| 2 | La Réunion | 23 669 | 411 | 57,6 |
| 3 | Guadeloupe | 7 187 | 207 | 34,7 |
| 4 | Yvelines | 118 208 | 3 614 | 32,7 |
| 5 | Hauts-de-Seine | 147 352 | 4 702 | 31,3 |
| 6 | Haute-Corse | 15 865 | 529 | 30,0 |
| 7 | Seine-Saint-Denis | 56 325 | 2 215 | 25,4 |
| 8 | Aisne | 25 374 | 1 004 | 25,3 |
| 9 | Val-d'Oise | 50 530 | 2 376 | 21,3 |
| 10 | Haute-Loire | 6 943 | 337 | 20,6 |

**Lecture :** ce classement brut mélange trois phénomènes différents. Il ne peut pas être présenté tel quel comme « les départements les plus sous-équipés ».

### H3 — Outre-mer : sous-déclaration des bornes 🔍

- **Observation :** les trois premiers rangs sont des départements d'outre-mer. La Martinique ne compte que 36 points de recharge déclarés pour 6 397 véhicules électriques.
- **Hypothèse :** la base nationale IRVE repose sur les déclarations des aménageurs. Celles-ci sont probablement moins complètes en outre-mer, ce qui crée un artefact de couverture plutôt qu'un vrai manque de bornes.
- **Test prévu :** comparer le nombre de points déclarés avec une source indépendante (données OpenStreetMap des bornes de recharge, ou publications des collectivités et syndicats d'énergie locaux).
- **Décision provisoire :** analyser **métropole et outre-mer séparément** dans le dashboard, avec un avertissement sur la couverture des données en outre-mer.

### H4 — Île-de-France : biais des flottes d'entreprise 🔍

- **Observation :** quatre départements franciliens dans le top 10 (Yvelines, Hauts-de-Seine, Seine-Saint-Denis, Val-d'Oise).
- **Hypothèse :** un véhicule est rattaché à l'adresse de son titulaire. Les sièges d'entreprises et de loueurs (location longue durée) y immatriculent de nombreux véhicules qui circulent dans toute la France, ce qui gonfle le nombre de VE locaux.
- **Test prévu :** mesurer la part des VE concentrée dans les communes signalées `suspicion_flotte` (plus de 2 voitures immatriculées par habitant) :

  ```sql
  SELECT nom_departement,
         COUNTIF(suspicion_flotte) AS communes_suspectes,
         SUM(IF(suspicion_flotte, nb_ve, 0)) AS ve_dans_communes_suspectes,
         SUM(nb_ve) AS ve_total
  FROM mart.v_tension_commune
  WHERE code_departement IN ('92', '78', '93', '95')
  GROUP BY nom_departement;
  ```

- **Critère de validation :** si une part importante des VE d'un département provient de quelques communes suspectes, l'hypothèse est confirmée et ces communes seront exclues d'un classement « corrigé ».
- **Résultat :**

  | Département | Communes suspectes | Part des VE dans ces communes | VE par point, brut | VE par point, hors communes suspectes* |
  |---|---:|---:|---:|---:|
  | Yvelines | 3 | **42 %** (50 171 / 118 208) | 32,7 | ≈ 18,8 |
  | Seine-Saint-Denis | 2 | **34 %** (18 888 / 56 325) | 25,4 | ≈ 16,9 |
  | Hauts-de-Seine | 3 | 20 % (29 164 / 147 352) | 31,3 | ≈ 25,1 |
  | Val-d'Oise | 1 | 16 % (7 922 / 50 530) | 21,3 | ≈ 17,9 |

  \* Estimation rapide : les VE des communes suspectes sont retirés, mais leurs bornes restent comptées. Le calcul exact est fait par la vue `v_tension_departement_corrigee`.

- **Conclusion :** hypothèse **partiellement validée**. Dans les Yvelines, 42 % des véhicules électriques sont immatriculés dans seulement 3 communes : le biais est massif et le classement brut est trompeur. En revanche, les **Hauts-de-Seine restent élevés après correction** (≈ 25 VE par point), d'où une nouvelle hypothèse H6.
- **📌 Décision :** création de la vue `v_tension_departement_corrigee` (`sql/04_classement_corrige.sql`), qui exclut les communes à suspicion de flotte (véhicules, bornes et population) et les départements d'outre-mer (H3). Elle indique pour chaque département combien de communes et de VE ont été exclus, pour que la correction reste transparente.

### H5 — Départements ruraux : vrai signal de sous-équipement 🔍

- **Observation :** Aisne, Haute-Loire et Haute-Corse apparaissent sans être concernés par les biais H3 ou H4.
- **Hypothèse :** ce sont de vrais territoires où l'infrastructure publique ne suit pas l'adoption des véhicules électriques. C'est le résultat que le projet cherche à mettre en évidence.
- **Test prévu :** une fois les corrections H3 et H4 appliquées, vérifier que ces départements restent en tête du classement « métropole, hors flottes ». Compléter avec la part de recharge rapide (> 50 kW), plus critique en zone rurale où les distances sont longues.

### H6 — Hauts-de-Seine : flottes sous le seuil de détection 🔍

- **Observation :** après exclusion des 3 communes suspectes, les Hauts-de-Seine gardent environ 25 VE par point, nettement au-dessus des autres départements franciliens corrigés.
- **Hypothèses concurrentes :**
  - (a) des sièges de flottes sont situés dans des communes très peuplées, où le ratio reste sous le seuil de 2 voitures par habitant et échappe donc à la détection ;
  - (b) la tension est réelle : département dense, fort taux d'équipement en VE, et recharge surtout privée (parkings d'immeubles et d'entreprises) non comptée dans la base des bornes publiques.
- **Test prévu :** lister les communes du département avec leur nombre de voitures par habitant et leur part de VE, et regarder si quelques communes concentrent une part anormale des VE.

---

## Prochaines étapes

1. ~~Exécuter le test H4~~ ✅ fait.
2. ~~Créer une vue de classement corrigé~~ ✅ fait (`v_tension_departement_corrigee`).
3. Consigner le nouveau top 10 corrigé et vérifier H5 (les départements ruraux restent-ils en tête ?).
4. Tester H6 sur les Hauts-de-Seine.
5. Construire le dashboard Power BI à partir des vues corrigées, avec les avertissements de couverture visibles.
