# Journal d'analyse

Ce journal trace la démarche suivie : ce qui a été observé, les hypothèses formulées, la façon dont elles ont été testées et les décisions qui en découlent. Il est tenu au fil du projet, y compris pour les pistes qui se sont révélées fausses.

**Légende des statuts :** ✅ validée · ❌ rejetée · 🔍 à vérifier · 📌 décision

---

## Synthèse des hypothèses

| # | Hypothèse | Statut |
|---|---|---|
| H1 | Les bornes non rattachées à une commune ont un code postal saisi à la place du code INSEE | ❌ rejetée (0,9 % seulement) |
| H2 | Ces bornes ont un code commune vide, mais des coordonnées GPS exploitables | ✅ validée (28,4 % récupérés sur les données finales) |
| H3 | Le classement de l'outre-mer reflète une sous-déclaration des bornes, pas un réel sous-équipement | 🔍 à vérifier |
| H4 | Les départements d'Île-de-France sont gonflés par les flottes d'entreprise et de loueurs | ✅ partiellement validée (Yvelines, Seine-Saint-Denis) |
| H5 | Les départements ruraux du classement (Aisne, Haute-Loire, Haute-Corse) sont de vrais territoires sous-équipés | ✅ partiellement validée (Haute-Loire oui ; Aisne et Haute-Corse non) |
| H6 | La tension résiduelle des Hauts-de-Seine vient de flottes non détectées par le seuil de 2 voitures par habitant | ✅ partiellement validée (immatriculations concentrées dans les communes d'affaires) |
| H8 | Certaines communes résidentielles des Hauts-de-Seine (Colombes, Antony) sont réellement sous-équipées | ✅ validée, et le phénomène dépasse les Hauts-de-Seine |
| H9 | La faible densité de bornes va de pair avec une faible adoption des VE, liée au profil des communes (revenus, type de logement) | 🔍 à vérifier (données externes nécessaires) |
| H7 | Aisne et Haute-Corse sortent du top 10 à cause d'une commune « flotte » (ex. loueurs près d'un aéroport) | ✅ validée (Villers-Cotterêts, Lucciana) |

---

## Semaine 1 — Qualité des données

> **Note sur les versions de données.** Le diagnostic ci-dessous a été mené le 8 octobre 2026 sur une première extraction de la base IRVE (170 624 points). Les données ont ensuite été retéléchargées le 28 octobre 2026 (177 956 points) : c'est cette version qui est chargée dans BigQuery et utilisée pour toutes les analyses des semaines 2 et suivantes. Les conclusions sont identiques, les chiffres à jour figurent dans le tableau ci-dessous et dans [`reports/qualite_donnees.md`](../reports/qualite_donnees.md).
>
> | Indicateur | 8 octobre (diagnostic) | 28 octobre (données finales) |
> |---|---:|---:|
> | Points de recharge (lignes brutes) | 170 624 | 177 956 |
> | Code commune vide | 44 606 | 50 267 |
> | Rattachés par code postal | 1 552 (0,9 %) | 1 432 (0,8 %) |
> | Rattachés par coordonnées GPS | 44 973 (26,4 %) | 50 622 (28,4 %) |
> | Non rattachés | 72 | 76 |
> | Dates de mise en service manquantes | 82 848 (49 %) | 83 674 (47 %) |

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

### 📌 Dates de mise en service manquantes (47 à 49 % selon la version)

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

### Classement corrigé (métropole, hors communes à suspicion de flotte)

Requête sur `mart.v_tension_departement_corrigee` :

| Rang | Département | Communes exclues | VE | Points | VE par point | Part de recharge rapide |
|---|---|---:|---:|---:|---:|---:|
| 1 | Hauts-de-Seine | 3 | 118 188 | 4 373 | 27,0 | 6,7 % |
| 2 | Haute-Loire | 1 | 6 942 | 337 | 20,6 | 15,4 % |
| 3 | Essonne | 1 | 58 060 | 2 855 | 20,3 | 24,9 % |
| 4 | Haut-Rhin | 1 | 35 594 | 1 763 | 20,2 | 29,0 % |
| 5 | Mayenne | 0 | 10 375 | 521 | 19,9 | 21,3 % |
| 6 | Val-d'Oise | 1 | 42 608 | 2 144 | 19,9 | 25,4 % |
| 7 | Yvelines | 3 | 68 037 | 3 451 | 19,7 | 19,7 % |
| 8 | Bouches-du-Rhône | 2 | 100 432 | 5 179 | 19,4 | 21,1 % |
| 9 | Var | 2 | 52 587 | 2 735 | 19,2 | 16,4 % |
| 10 | Isère | 1 | 55 314 | 2 888 | 19,2 | 25,2 % |

**Lecture :**

- **Les écarts se resserrent fortement.** Le classement brut allait de 20 à 178 VE par point ; une fois les biais retirés, le top 10 tient entre 19 et 27. Le premier « classement des départements sous-équipés » était donc surtout un classement des **biais de données**.
- **H5 partiellement validée.** La **Haute-Loire** reste 2ᵉ : c'est un vrai signal. La **Mayenne** apparaît au 5ᵉ rang **sans aucune commune exclue**, ce qui en fait le signal le plus « propre » du classement. En revanche, **l'Aisne et la Haute-Corse sortent du top 10** : leur position venait aussi d'une commune à suspicion de flotte (hypothèse H7).
- **Hauts-de-Seine : cas à part.** Il reste 1ᵉʳ avec 27 VE par point, et surtout la **plus faible part de recharge rapide du top 10 (6,7 %)**, quatre fois moins que le Haut-Rhin (29 %). Cela nourrit la piste (b) de H6 : un réseau public dense en ville mais composé de bornes lentes, avec une recharge qui se fait surtout en privé.
- **Nouvel angle :** puisque le nombre de VE par point varie peu après correction, **la part de recharge rapide** devient un indicateur discriminant pour le dashboard (de 6,7 % à 29 % dans ce seul top 10).

### H7 — Aisne et Haute-Corse : une commune « flotte » 🔍

- **Observation :** ces deux départements sortent du top 10 après correction, avec 1 commune exclue chacun (Haute-Corse : rang 6 brut à hors top 10).
- **Piste :** en Haute-Corse, la presse spécialisée cite **Lucciana**, commune de l'aéroport de Bastia, comme ayant plus de voitures immatriculées que d'habitants, du fait des loueurs ([Tesla Mag](https://www.tesla-mag.com/voitures-electriques-par-commune-carte-france/)).
- **Test prévu :** lister les communes exclues et vérifier qu'elles correspondent bien à des sièges de flottes ou de loueurs :

  ```sql
  SELECT nom_departement, nom_commune, population, nb_vp, nb_ve,
         ROUND(SAFE_DIVIDE(nb_vp, population), 1) AS voitures_par_habitant
  FROM mart.v_tension_commune
  WHERE suspicion_flotte AND code_departement IN ('02', '2B', '92')
  ORDER BY nom_departement, nb_ve DESC;
  ```

**Résultat du test H7 :**

| Département | Commune | Population | Voitures immatriculées | dont VE | Voitures par habitant |
|---|---|---:|---:|---:|---:|
| Aisne | Villers-Cotterêts | 10 489 | 53 315 | 11 318 | 5,1 |
| Haute-Corse | Lucciana | 6 923 | 34 273 | 8 198 | 5,0 |
| Haute-Corse | Tox | 96 | 1 536 | 81 | 16,0 |
| Haute-Corse | Tallone, Morsiglia, Campi, Muro, Piobetta | 19 à 288 | 40 à 585 | 0 à 23 | 2,0 à 2,1 |
| Hauts-de-Seine | Rueil-Malmaison | 82 874 | 263 209 | 17 850 | 3,2 |
| Hauts-de-Seine | Clichy | 64 410 | 160 451 | 9 685 | 2,5 |
| Hauts-de-Seine | Vaucresson | 8 432 | 26 691 | 1 629 | 3,2 |

- **H7 validée.** Deux communes concentrent à elles seules l'essentiel du biais : **Villers-Cotterêts** (5 voitures par habitant, 11 318 VE pour 10 489 habitants) dans l'Aisne, et **Lucciana** (5 voitures par habitant), commune de l'aéroport de Bastia, en Haute-Corse. Ces volumes ne peuvent pas correspondre aux seuls résidents : ce sont des immatriculations de flottes ou de loueurs.
- **Dans les Hauts-de-Seine**, Rueil-Malmaison compte à elle seule 263 209 voitures immatriculées pour 82 874 habitants.

### 📌 Affinage du seuil de détection des flottes

- **Constat :** le seuil « plus de 2 voitures par habitant » signale aussi **de très petits villages corses** (19 à 288 habitants, 0 à 23 VE). Sur de si petites populations, le ratio est instable : quelques résidents secondaires suffisent à le faire dépasser 2. Ce ne sont pas des flottes.
- **Impact :** négligeable sur les résultats (moins de 100 VE au total), mais c'est un défaut de méthode.
- **Décision :** le critère devient « **plus de 2 voitures par habitant ET au moins 1 000 voitures immatriculées** » (`sql/03_analyses.sql`). Tox (1 536 voitures pour 96 habitants) reste signalée, les autres petits villages ne le sont plus.

### Résultat du test H6 (Hauts-de-Seine, 15 communes ayant le plus de VE)

Après application du nouveau seuil, seules Rueil-Malmaison et Clichy restent signalées comme flottes dans le département. Calculs à partir de `v_tension_commune` :

| Commune | Voitures par habitant | Part de VE dans le parc | Points pour 10 000 hab. | VE par point |
|---|---:|---:|---:|---:|
| Rueil-Malmaison *(flotte)* | 3,18 | 6,8 % | 32,7 | 65,9 |
| Courbevoie | 1,36 | 15,3 % | 32,6 | 63,9 |
| Boulogne-Billancourt | 0,94 | 11,9 % | 28,2 | 39,4 |
| Issy-les-Moulineaux | 0,90 | **20,9 %** | 36,9 | 51,0 |
| Nanterre | 1,11 | 10,8 % | 16,1 | 74,4 |
| Clichy *(flotte)* | 2,49 | 6,0 % | 6,1 | 248,3 |
| Puteaux | 1,65 | 12,9 % | 128,6 | 16,6 |
| Levallois-Perret | 0,81 | 11,0 % | 54,5 | 16,4 |
| Neuilly-sur-Seine | 0,88 | 11,4 % | 102,3 | 9,7 |
| Gennevilliers | 0,95 | 8,9 % | 28,6 | 29,7 |
| Châtenay-Malabry | 0,88 | 12,2 % | 15,4 | 69,7 |
| Antony | 0,81 | 5,6 % | **7,9** | 57,1 |
| Meudon | 0,78 | 7,5 % | 17,3 | 34,3 |
| Colombes | 0,68 | 4,2 % | **5,9** | 48,8 |
| Asnières-sur-Seine | 0,60 | 4,4 % | 13,4 | 19,5 |

**Lecture :**

- **Deux profils de communes se dégagent.** Les communes résidentielles (Colombes, Asnières, Antony) ont une part de VE de **4 à 6 %**. Les communes de quartiers d'affaires (Issy-les-Moulineaux, Courbevoie, Puteaux, Boulogne-Billancourt, Nanterre) atteignent **11 à 21 %**, avec souvent plus d'une voiture par habitant.
- **Interprétation :** ces écarts sont cohérents avec des véhicules de société immatriculés à l'adresse des entreprises, sans atteindre le seuil de 2 voitures par habitant. Les données ne permettent pas de le prouver formellement : il n'y a pas de distinction particulier / entreprise à la maille communale.
- **H6 partiellement validée :** le nombre de VE « locaux » des Hauts-de-Seine est vraisemblablement surestimé par des flottes diffuses. Le premier rang du département dans le classement corrigé n'est donc pas fiable.
- **Les deux communes signalées comme flottes ont une faible part de VE (6 à 7 %)**, à l'inverse des communes d'affaires. Ce sont probablement deux types de flottes différents (loueurs et parcs anciens d'un côté, véhicules de société récents de l'autre). C'est une hypothèse, non testée.

### 📌 Décision : deux indicateurs complémentaires, et non un seul

- **Constat :** le nombre de VE par point dépend des immatriculations, que l'on ne peut pas entièrement corriger des flottes avec ces données.
- **Décision :** le dashboard présentera **deux indicateurs côte à côte** :
  - **VE par point de recharge** : mesure la tension, mais reste sensible aux flottes (avertissement affiché) ;
  - **Points de recharge pour 10 000 habitants** : mesure l'équipement rapporté à la population résidente, **indépendant des immatriculations** et donc insensible aux flottes.
- **Ajout au modèle :** colonnes `part_ve_dans_parc` et `voitures_par_habitant` dans `v_tension_commune`, pour visualiser ces profils dans le dashboard.

### H8 — Communes résidentielles réellement sous-équipées 🔍

- **Observation :** **Colombes** (91 000 habitants, 54 points, **5,9 points pour 10 000 habitants**) et **Antony** (64 000 habitants, 51 points, **7,9**) ont une densité de bornes très inférieure à leurs voisines, par exemple Neuilly-sur-Seine (102) ou Puteaux (129). Ce sont des communes résidentielles, peu concernées par le biais des flottes.
- **Hypothèse :** ce sont de vrais déserts relatifs de recharge publique en zone dense, où beaucoup d'habitants n'ont pas de place de parking privée pour recharger chez eux.
- **Test prévu :** classer toutes les communes de plus de 30 000 habitants selon les points pour 10 000 habitants, et vérifier si ce profil se retrouve ailleurs en Île-de-France et en France.

### Résultat du test H8 (communes de plus de 30 000 habitants, hors flottes)

**Anomalie détectée au passage :** les deux premières lignes étaient **Nouméa et Dumbéa (Nouvelle-Calédonie)**, avec une part de VE vide. Leur code département commence par `98`, et non `97` : le filtre « métropole » ne les excluait pas. La Nouvelle-Calédonie n'est d'ailleurs pas couverte par les données d'immatriculation. 📌 **Correction :** le filtre exclut désormais les codes `97x` **et** `98x` (`sql/04_classement_corrige.sql`). Effet nul sur le classement corrigé (sans VE, ces communes étaient en bas de classement), mais le filtre est maintenant juste. La requête relancée avec ce filtre ne renvoie plus que des communes métropolitaines.

Les 15 communes métropolitaines les moins équipées (requête relancée avec le filtre corrigé) :

| Commune | Département | Population | Points | Points pour 10 000 hab. | Part de VE |
|---|---|---:|---:|---:|---:|
| Vitry-sur-Seine | Val-de-Marne | 93 963 | 20 | **2,1** | 2,3 % |
| Gagny | Seine-Saint-Denis | 42 313 | 14 | 3,3 | 2,6 % |
| Villiers-le-Bel | Val-d'Oise | 30 053 | 10 | 3,3 | 1,4 % |
| Maisons-Alfort | Val-de-Marne | 56 799 | 22 | 3,9 | 4,8 % |
| Saint-Médard-en-Jalles | Gironde | 32 910 | 13 | 4,0 | 4,7 % |
| Creil | Oise | 36 301 | 17 | 4,7 | 1,2 % |
| Meyzieu | Rhône | 36 687 | 20 | 5,5 | 4,0 % |
| Villeneuve-Saint-Georges | Val-de-Marne | 36 221 | 20 | 5,5 | 1,6 % |
| Ris-Orangis | Essonne | 31 189 | 17 | 5,5 | 2,3 % |
| Argenteuil | Val-d'Oise | 106 130 | 59 | 5,6 | 2,4 % |
| Vigneux-sur-Seine | Essonne | 31 466 | 18 | 5,7 | 2,2 % |
| Épinay-sur-Seine | Seine-Saint-Denis | 52 833 | 31 | 5,9 | 1,6 % |
| Colombes | Hauts-de-Seine | 91 053 | 54 | 5,9 | 4,2 % |
| Saint-Denis | Seine-Saint-Denis | 149 077 | 90 | 6,0 | 4,1 % |
| Clamart | Hauts-de-Seine | 58 576 | 36 | 6,1 | 5,3 % |

À titre de comparaison : Neuilly-sur-Seine compte 102 points pour 10 000 habitants, et Puteaux 129.

**Lecture :**

- **H8 validée, et elle dépasse les Hauts-de-Seine.** **12 des 15 communes** sont en Île-de-France, surtout dans le Val-de-Marne, la Seine-Saint-Denis, le Val-d'Oise et l'Essonne. Vitry-sur-Seine compte **20 points de recharge pour près de 94 000 habitants**, soit 60 fois moins par habitant que Puteaux.
- **Ces communes ont aussi une très faible part de VE (1,2 à 4,8 %).** Leur ratio « VE par point » n'est donc pas alarmant : c'est précisément pourquoi elles n'apparaissaient pas dans les classements par tension. Le manque de bornes y est **une barrière à l'adoption à venir**, plus qu'une saturation actuelle.
- **C'est le résultat principal du projet :** les vrais déserts de recharge publique ne sont pas les départements en tête du classement brut, mais de **grandes communes de banlieue**, denses, où beaucoup d'habitants vivent en logement collectif et ne peuvent probablement pas recharger chez eux.

### H9 — Densité de bornes, adoption des VE et profil des communes 🔍

- **Observation :** les communes les moins équipées sont aussi celles où la part de VE est la plus faible.
- **Hypothèse :** les deux sont liés au profil socio-économique des communes (revenus, part de logement collectif sans parking privé). Le sens de la causalité reste ouvert : peu de bornes freinent l'achat de VE, et peu de VE découragent l'installation de bornes.
- **Test possible (extension du projet) :** croiser avec les données de l'INSEE (revenu médian par commune, part de logements collectifs) et mesurer la corrélation. Hors du périmètre actuel, mais c'est l'enrichissement le plus naturel.

---

## Prochaines étapes

1. ~~Exécuter le test H4~~ ✅ fait.
2. ~~Créer une vue de classement corrigé~~ ✅ fait (`v_tension_departement_corrigee`).
3. ~~Consigner le top 10 corrigé et vérifier H5~~ ✅ fait.
4. ~~Tester H7~~ ✅ fait, seuil de détection affiné.
5. ~~Tester H6~~ ✅ fait : décision de présenter deux indicateurs complémentaires.
6. ~~Tester H8~~ ✅ fait : résultat principal du projet identifié.
7. Construire le dashboard Power BI à partir des vues corrigées, avec les avertissements de couverture visibles.
