"""Étape 1 — Ingestion : télécharge les sources brutes dans data/raw/.

Usage :
    python src/ingest.py            # télécharge ce qui manque
    python src/ingest.py --force    # retélécharge tout (nouvelle version des données)
"""

import argparse
import json
import sys
from datetime import datetime, timezone

import requests

from config import RAW_DIR, SOURCES

CHUNK_SIZE = 1024 * 1024  # 1 Mo
TIMEOUT = 60


def obsolete(target, source: dict) -> bool:
    """Vrai si le fichier local date d'une ancienne version du projet (champs manquants)."""
    champs = source.get("champs_requis")
    if not champs:
        return False
    contenu = target.read_text(encoding="utf-8", errors="ignore")
    return not all(c in contenu for c in champs)


def download(name: str, source: dict, force: bool = False) -> None:
    target = RAW_DIR / source["filename"]
    if target.exists() and not force and not obsolete(target, source):
        print(f"[{name}] déjà présent ({target.stat().st_size / 1e6:.1f} Mo) — ignoré")
        return

    print(f"[{name}] téléchargement : {source['description']}")
    tmp = target.with_suffix(target.suffix + ".part")
    with requests.get(source["url"], stream=True, timeout=TIMEOUT) as resp:
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        done = 0
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(CHUNK_SIZE):
                f.write(chunk)
                done += len(chunk)
                if total:
                    print(f"\r  {done / 1e6:6.1f} / {total / 1e6:.1f} Mo", end="")
    tmp.replace(target)  # écriture atomique : pas de fichier à moitié téléchargé
    print(f"\n[{name}] OK -> {target.name}")


def write_manifest() -> None:
    """Trace la date et la provenance de chaque fichier (traçabilité / gouvernance)."""
    manifest = {
        name: {
            "fichier": src["filename"],
            "source": src["page"],
            "telecharge_le": datetime.fromtimestamp(
                (RAW_DIR / src["filename"]).stat().st_mtime, tz=timezone.utc
            ).isoformat(timespec="seconds"),
        }
        for name, src in SOURCES.items()
        if (RAW_DIR / src["filename"]).exists()
    }
    (RAW_DIR / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="retélécharger tout")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    errors = 0
    for name, source in SOURCES.items():
        try:
            download(name, source, force=args.force)
        except requests.RequestException as exc:
            errors += 1
            print(f"[{name}] ÉCHEC : {exc}", file=sys.stderr)
    write_manifest()
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
