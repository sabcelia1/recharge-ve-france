"""Configuration centrale du projet : sources de données et chemins."""

from pathlib import Path

# --- Chemins -----------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = ROOT_DIR / "reports"

# --- Sources (open data, Licence Ouverte) --------------------------------------
# Les URL "latest" de data.gouv.fr pointent toujours vers la dernière version
# du fichier : pas besoin de les mettre à jour à chaque publication.
SOURCES = {
    "irve": {
        "description": "Base nationale consolidée IRVE - données statiques "
                       "(Point d'Accès National transport.data.gouv.fr)",
        "url": "https://www.data.gouv.fr/api/1/datasets/r/4ca78c71-4ea4-475d-bd3a-d4aef88f7bf8",
        "page": "https://www.data.gouv.fr/datasets/beta-bases-nationales-des-points-de-recharge-pour-vehicules-electriques-en-france-irve",
        "filename": "irve_statique.csv",
    },
    "vehicules": {
        "description": "Voitures particulières immatriculées par commune et par "
                       "type de recharge (Agence ORE / AAA Data), trimestriel",
        "url": "https://www.data.gouv.fr/api/1/datasets/r/90e0d717-deda-4bdc-9987-f82faac5bc93",
        "page": "https://www.data.gouv.fr/datasets/voitures-particulieres-immatriculees-par-commune-et-par-type-de-recharge-jeu-de-donnees-aaadata",
        "filename": "vehicules_par_commune.csv",
    },
    "communes": {
        "description": "Référentiel des communes avec population (API Découpage "
                       "administratif, geo.api.gouv.fr)",
        "url": "https://geo.api.gouv.fr/communes"
               "?fields=nom,code,codeDepartement,codeRegion,population,codesPostaux,centre&format=json",
        # Champs indispensables : si le fichier local ne les contient pas, il est retéléchargé.
        "champs_requis": ['"codesPostaux"', '"centre"'],
        "page": "https://geo.api.gouv.fr/decoupage-administratif",
        "filename": "communes.json",
    },
}

# --- Règles métier -------------------------------------------------------------
# Paliers de puissance (kW) utilisés dans tout le projet.
PUISSANCE_PALIERS = [
    (0, 7.4, "Lente (≤ 7,4 kW)"),
    (7.4, 22, "Accélérée (7,4–22 kW)"),
    (22, 50, "Rapide (22–50 kW)"),
    (50, 150, "Très rapide (50–150 kW)"),
    (150, float("inf"), "Ultra-rapide (> 150 kW)"),
]

# Arrondissements municipaux -> commune "parente", pour harmoniser les jointures
# (certaines sources codent Paris/Lyon/Marseille par arrondissement).
ARRONDISSEMENTS = {
    **{f"751{i:02d}": "75056" for i in range(1, 21)},   # Paris
    **{f"6938{i}": "69123" for i in range(1, 10)},      # Lyon
    **{f"132{i:02d}": "13055" for i in range(1, 17)},   # Marseille
}
