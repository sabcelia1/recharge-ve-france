"""Étape 2 — Nettoyage : transforme data/raw/ en tables propres dans data/processed/.

Produit :
    data/processed/points_recharge.parquet   1 ligne = 1 point de recharge
    data/processed/vehicules.parquet         1 ligne = 1 commune x 1 trimestre
    data/processed/communes.parquet          référentiel communes + population
    reports/qualite_donnees.md               rapport de qualité (contrôles chiffrés)

Usage :
    python src/clean.py
"""

import json
import sys

import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from config import ARRONDISSEMENTS, PROCESSED_DIR, PUISSANCE_PALIERS, RAW_DIR, REPORTS_DIR, SOURCES

RAYON_TERRE_KM = 6371

# Journal des contrôles qualité, alimenté au fil du nettoyage.
QUALITE: list[tuple[str, str, str]] = []


def log(table: str, controle: str, resultat) -> None:
    QUALITE.append((table, controle, str(resultat)))
    print(f"  [{table}] {controle} : {resultat}")


def normaliser_code_insee(serie: pd.Series) -> pd.Series:
    """Code INSEE sur 5 caractères (gère 1001 -> 01001 et la Corse 2A/2B),
    arrondissements de Paris/Lyon/Marseille ramenés à la commune."""
    codes = serie.astype("string").str.strip().str.upper().str.zfill(5)
    codes = codes.where(codes.str.fullmatch(r"\d{5}|2[AB]\d{3}"))
    return codes.replace(ARRONDISSEMENTS)


def classer_puissance(kw: pd.Series) -> pd.Series:
    bornes = [p[0] for p in PUISSANCE_PALIERS] + [PUISSANCE_PALIERS[-1][1]]
    labels = [p[2] for p in PUISSANCE_PALIERS]
    return pd.cut(kw, bins=bornes, labels=labels, right=True, include_lowest=True)


# --- Communes ------------------------------------------------------------------
def nettoyer_communes() -> pd.DataFrame:
    print("\n== Communes")
    data = json.loads((RAW_DIR / SOURCES["communes"]["filename"]).read_text(encoding="utf-8"))
    df = pd.DataFrame(data).rename(columns={
        "code": "code_insee", "nom": "nom_commune",
        "codeDepartement": "code_departement", "codeRegion": "code_region",
    })
    log("communes", "lignes", f"{len(df):,}")
    log("communes", "population manquante", int(df["population"].isna().sum()))
    df["population"] = df["population"].astype("Int64")
    if not {"codesPostaux", "centre"} <= set(df.columns):
        raise SystemExit("communes.json est incomplet : supprimez data/raw/communes.json "
                         "puis relancez src/ingest.py")
    # centre = point GeoJSON {"type": "Point", "coordinates": [lon, lat]}
    coords = df["centre"].map(lambda c: c["coordinates"] if isinstance(c, dict) else [None, None])
    df["centre_lon"] = coords.str[0].astype(float)
    df["centre_lat"] = coords.str[1].astype(float)
    return df[["code_insee", "nom_commune", "code_departement", "code_region",
               "population", "codesPostaux", "centre_lon", "centre_lat"]]


def vers_xyz(lon, lat) -> np.ndarray:
    """Coordonnées GPS -> points 3D sur la sphère unité (distances exactes partout,
    y compris en outre-mer, contrairement à un calcul sur lon/lat brutes)."""
    lon, lat = np.radians(np.asarray(lon, float)), np.radians(np.asarray(lat, float))
    return np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])


def commune_la_plus_proche(communes: pd.DataFrame, lon: pd.Series, lat: pd.Series,
                           distance_max_km: float = 15) -> pd.Series:
    """Code INSEE de la commune dont le centre est le plus proche de chaque point.
    Au-delà de distance_max_km, on ne rattache pas (coordonnées probablement erronées)."""
    ref = communes.dropna(subset=["centre_lon", "centre_lat"])
    arbre = cKDTree(vers_xyz(ref["centre_lon"], ref["centre_lat"]))
    distance, indice = arbre.query(vers_xyz(lon, lat))
    distance_km = distance * RAYON_TERRE_KM  # corde ≈ arc à cette échelle
    codes = ref["code_insee"].to_numpy()[indice]
    return pd.Series(codes, index=lon.index, dtype="string").where(distance_km <= distance_max_km)


def table_codes_postaux(communes: pd.DataFrame) -> dict[str, str]:
    """Code postal -> code INSEE. Quand un code postal couvre plusieurs communes,
    on retient la plus peuplée (même département : sans effet à la maille départementale)."""
    cp = (communes[["code_insee", "population", "codesPostaux"]]
          .explode("codesPostaux").dropna(subset=["codesPostaux"])
          .sort_values("population", ascending=False, na_position="last")
          .drop_duplicates("codesPostaux"))
    return dict(zip(cp["codesPostaux"], cp["code_insee"]))


def rattacher_commune(codes: pd.Series, lon: pd.Series, lat: pd.Series,
                      communes: pd.DataFrame, table: str) -> tuple[pd.Series, pd.Series]:
    """Rattache chaque point de recharge à un code INSEE valide, par ordre de fiabilité :
    1. code INSEE déclaré, s'il existe dans le référentiel ;
    2. code postal saisi à la place du code INSEE ;
    3. coordonnées GPS -> commune dont le centre est le plus proche.
    La méthode utilisée est conservée pour chaque ligne (traçabilité)."""
    codes_valides = set(communes["code_insee"])
    cp_vers_insee = table_codes_postaux(communes)

    brut = codes.astype("string").str.strip().str.upper().str.zfill(5)
    normalise = normaliser_code_insee(codes)
    resultat = normalise.where(normalise.isin(codes_valides))
    methode = pd.Series("code INSEE", index=codes.index, dtype="object").where(resultat.notna())

    # Diagnostic : à quoi ressemblent les codes non reconnus ?
    non_reconnus = codes[resultat.isna()]
    log(table, "code commune déclaré vide", f"{int(non_reconnus.isna().sum()):,}")
    exemples = non_reconnus.dropna().value_counts().head(5)
    if len(exemples):
        log(table, "codes non reconnus les plus fréquents",
            ", ".join(f"'{c}' ({n})" for c, n in exemples.items()))

    via_cp = resultat.isna() & brut.isin(cp_vers_insee.keys())
    resultat[via_cp] = brut[via_cp].map(cp_vers_insee)
    methode[via_cp] = "code postal corrigé"

    via_gps = resultat.isna() & lon.notna() & lat.notna()
    if via_gps.any():
        proches = commune_la_plus_proche(communes, lon[via_gps], lat[via_gps])
        resultat[via_gps] = proches
        methode[via_gps & resultat.notna()] = "coordonnées GPS"

    methode = methode.fillna("non rattaché")
    for m, n in methode.value_counts().items():
        log(table, f"rattachement commune — {m}", f"{n:,} ({n / len(methode):.1%})")
    return resultat, methode


# --- Points de recharge (IRVE) -----------------------------------------------------
def nettoyer_irve(communes: pd.DataFrame) -> pd.DataFrame:
    print("\n== Points de recharge (IRVE)")
    colonnes = [
        "id_pdc_itinerance", "id_station_itinerance", "nom_station", "nom_operateur",
        "implantation_station", "code_insee_commune", "puissance_nominale",
        "prise_type_combo_ccs", "prise_type_2", "gratuit", "condition_acces",
        "date_mise_en_service", "consolidated_longitude", "consolidated_latitude",
    ]
    df = pd.read_csv(
        RAW_DIR / SOURCES["irve"]["filename"],
        usecols=lambda c: c in colonnes,
        dtype={"code_insee_commune": "string", "id_pdc_itinerance": "string"},
        low_memory=False,
    )
    log("irve", "lignes brutes", f"{len(df):,}")

    # 1. Doublons sur l'identifiant du point de recharge
    avant = len(df)
    df = df.drop_duplicates(subset="id_pdc_itinerance", keep="first")
    log("irve", "doublons id_pdc_itinerance supprimés", f"{avant - len(df):,}")

    # 2. Puissance : certains producteurs saisissent en W au lieu de kW
    df["puissance_nominale"] = pd.to_numeric(df["puissance_nominale"], errors="coerce")
    en_watts = df["puissance_nominale"] > 1000
    log("irve", "puissances saisies en W (converties en kW)", int(en_watts.sum()))
    df.loc[en_watts, "puissance_nominale"] /= 1000
    aberrantes = ~df["puissance_nominale"].between(1, 1000)
    log("irve", "puissances manquantes ou aberrantes (mises à vide)", int(aberrantes.sum()))
    df.loc[aberrantes, "puissance_nominale"] = pd.NA
    df["palier_puissance"] = classer_puissance(df["puissance_nominale"])

    # 3. Dates de mise en service
    df["date_mise_en_service"] = pd.to_datetime(df["date_mise_en_service"], errors="coerce")
    futures = df["date_mise_en_service"] > pd.Timestamp.today()
    anciennes = df["date_mise_en_service"] < pd.Timestamp("2010-01-01")
    log("irve", "dates manquantes ou illisibles", int(df["date_mise_en_service"].isna().sum()))
    log("irve", "dates incohérentes (avant 2010 ou futures, mises à vide)",
        int((futures | anciennes).sum()))
    df.loc[futures | anciennes, "date_mise_en_service"] = pd.NaT

    # 4. Code commune : normalisation + contrôle contre le référentiel
    for col in ("consolidated_longitude", "consolidated_latitude"):
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["code_insee"], df["methode_rattachement"] = rattacher_commune(
        df["code_insee_commune"], df["consolidated_longitude"], df["consolidated_latitude"],
        communes, "irve")

    return df.drop(columns=["code_insee_commune"]).rename(columns={
        "consolidated_longitude": "longitude", "consolidated_latitude": "latitude",
    })


# --- Véhicules -------------------------------------------------------------------
def nettoyer_vehicules(codes_valides: set[str]) -> pd.DataFrame:
    print("\n== Véhicules immatriculés")
    chemin = RAW_DIR / SOURCES["vehicules"]["filename"]
    # Le séparateur (',' ou ';') et l'encodage (UTF-8 ou Windows-1252) varient selon
    # l'export : détection automatique du séparateur, essai des deux encodages.
    for encodage in ("utf-8", "cp1252", "latin-1"):
        try:
            df = pd.read_csv(chemin, sep=None, engine="python", encoding=encodage,
                             dtype={"CODGEO": "string"})
            break
        except UnicodeDecodeError:
            continue
    log("vehicules", "encodage détecté", encodage)
    log("vehicules", "lignes brutes", f"{len(df):,}")

    df = df.rename(columns={
        "CODGEO": "code_insee", "LIBGEO": "nom_commune", "DATE_ARRETE": "date_arrete",
        "NB_VP_RECHARGEABLES_EL": "nb_vp_electriques",
        "NB_VP_RECHARGEABLES_GAZ": "nb_vp_gaz", "NB_VP": "nb_vp_total",
    })
    df["code_insee"] = normaliser_code_insee(df["code_insee"])
    df["date_arrete"] = pd.to_datetime(df["date_arrete"], errors="coerce")

    # Contrôle avant agrégation, pour ne pas masquer une ligne incohérente
    incoherents = df["nb_vp_electriques"] > df["nb_vp_total"]
    log("vehicules", "lignes où VE > total (incohérentes, exclues)", int(incoherents.sum()))
    df = df[~incoherents]

    # Arrondissements ramenés à la commune -> on ré-agrège
    df = (df.groupby(["code_insee", "date_arrete"], as_index=False)
            [["nb_vp_electriques", "nb_vp_gaz", "nb_vp_total"]].sum())

    log("vehicules", "trimestres couverts",
        f"{df['date_arrete'].min():%Y-%m} → {df['date_arrete'].max():%Y-%m} "
        f"({df['date_arrete'].nunique()} trimestres)")
    inconnus = ~df["code_insee"].isin(codes_valides)
    log("vehicules", "codes INSEE absents du référentiel communes",
        f"{int(inconnus.sum()):,} ({inconnus.mean():.1%})")
    return df


# --- Rapport -----------------------------------------------------------------------
def ecrire_rapport() -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    lignes = [
        "# Rapport de qualité des données",
        "",
        f"_Généré automatiquement par `src/clean.py` le {pd.Timestamp.today():%d/%m/%Y}._",
        "",
        "| Table | Contrôle | Résultat |",
        "|---|---|---|",
        *[f"| {t} | {c} | {r} |" for t, c, r in QUALITE],
        "",
    ]
    (REPORTS_DIR / "qualite_donnees.md").write_text("\n".join(lignes), encoding="utf-8")


def main() -> int:
    manquants = [s["filename"] for s in SOURCES.values() if not (RAW_DIR / s["filename"]).exists()]
    if manquants:
        print(f"Fichiers manquants dans data/raw/ : {manquants}. Lancez d'abord src/ingest.py",
              file=sys.stderr)
        return 1

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    communes = nettoyer_communes()
    codes = set(communes["code_insee"])
    irve = nettoyer_irve(communes)
    vehicules = nettoyer_vehicules(codes)
    communes = communes.drop(columns=["codesPostaux"])

    communes.to_parquet(PROCESSED_DIR / "communes.parquet", index=False)
    irve.to_parquet(PROCESSED_DIR / "points_recharge.parquet", index=False)
    vehicules.to_parquet(PROCESSED_DIR / "vehicules.parquet", index=False)
    ecrire_rapport()
    print(f"\nTerminé : tables dans {PROCESSED_DIR}, rapport dans reports/qualite_donnees.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
