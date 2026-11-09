"""Génère les fonds de page du dashboard Power BI (HTML -> PNG 2560x1440).

Chaque fond contient le bandeau, les titres, les messages clés et les panneaux
blancs sur lesquels se posent les visuels Power BI (fond transparent).
Les positions des visuels sont dans POSITIONS (en pixels, page Power BI 1280x720).

Usage :
    python generer_fonds.py            # écrit html/*.html
    node capture.js                    # convertit en png/*.png
"""

import json
from pathlib import Path

ICI = Path(__file__).parent
ICONES = ICI.parent / "icones"

NAVY, TEAL, TEAL_L, AMBER, GREY, BG, LINE = (
    "#14213D", "#0E9F8E", "#E3F5F2", "#F2A541", "#5B6676", "#EEF2F6", "#DDE3EA")


EXTRA = {  # pictogrammes supplémentaires pour la page Méthode
    "base": '<ellipse cx="32" cy="14" rx="18" ry="6"/><path d="M14 14 V50 Q14 56 32 56 Q50 56 50 50 V14"/><path d="M14 26 Q14 32 32 32 Q50 32 50 26"/><path d="M14 38 Q14 44 32 44 Q50 44 50 38"/>',
    "code": '<path d="M22 18 L8 32 L22 46"/><path d="M42 18 L56 32 L42 46"/><path d="M36 12 L28 52"/>',
    "graphique": '<path d="M8 56 H56"/><rect x="12" y="34" width="9" height="16" rx="2"/><rect x="27.5" y="22" width="9" height="28" rx="2"/><rect x="43" y="12" width="9" height="38" rx="2"/>',
    "fichier": '<path d="M16 6 H38 L50 18 V58 H16 Z"/><path d="M38 6 V18 H50"/><path d="M23 30 H43"/><path d="M23 40 H43"/><path d="M23 50 H35"/>',
}
COULEURS = {"vert": TEAL, "bleu": NAVY, "blanc": "#FFFFFF"}


def icone(nom, couleur="vert", taille=28):
    """SVG en ligne, couleur portée par des attributs (pas de <style> global
    qui s'appliquerait à toutes les icônes de la page)."""
    import re
    col = COULEURS[couleur]
    if nom in EXTRA:
        corps = EXTRA[nom]
    else:
        svg = (ICONES / f"{nom}_{couleur}.svg").read_text(encoding="utf-8")
        corps = re.sub(r"<svg[^>]*>|</svg>|<style>.*?</style>", "", svg, flags=re.S)
    corps = corps.replace('class="f"', f'fill="{col}"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="{taille}" height="{taille}" '
            f'fill="none" stroke="{col}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">{corps}</svg>')


CSS = f"""
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ width:1280px; height:720px; background:{BG}; font-family:'Inter',sans-serif;
        color:{NAVY}; position:relative; overflow:hidden; }}
.abs {{ position:absolute; }}
.header {{ left:0; top:0; width:1280px; height:76px; background:{NAVY}; }}
.header::after {{ content:''; position:absolute; left:0; bottom:0; width:1280px; height:3px;
        background:linear-gradient(90deg,{TEAL} 0%,{TEAL} 30%,{AMBER} 30%,{AMBER} 34%,transparent 34%); }}
.titre {{ left:32px; top:14px; color:#fff; font-size:24px; font-weight:700; letter-spacing:-0.3px; }}
.soustitre {{ left:32px; top:47px; color:#8FD9CF; font-size:12.5px; font-weight:500; }}
.region-lbl {{ left:946px; top:28px; color:#fff; font-size:13px; font-weight:600;
        display:flex; align-items:center; gap:8px; }}
.slot-slicer {{ left:1032px; top:20px; width:216px; height:36px; background:#fff; border-radius:8px; }}
.panel {{ background:#fff; border-radius:14px; box-shadow:0 2px 10px rgba(20,33,61,0.07);
        border:1px solid {LINE}; }}
.ptitre {{ font-size:14px; font-weight:700; }}
.psous {{ font-size:11px; color:{GREY}; margin-top:3px; }}
.footer {{ left:32px; top:699px; width:1216px; font-size:10px; color:#8A94A3;
        display:flex; justify-content:space-between; }}
.kpi-ico {{ width:52px; height:52px; border-radius:50%; background:{TEAL_L};
        display:flex; align-items:center; justify-content:center; }}
.kpi-lbl {{ font-size:11px; font-weight:700; color:{GREY}; letter-spacing:0.6px; text-transform:uppercase; }}
.kpi-cap {{ font-size:10.5px; color:#8A94A3; }}
.callout {{ display:flex; align-items:center; gap:20px; padding:0 24px; overflow:hidden; }}
.callout::before {{ content:''; position:absolute; left:0; top:0; bottom:0; width:6px;
        background:{AMBER}; border-radius:14px 0 0 14px; }}
.big {{ font-size:34px; font-weight:800; color:{AMBER}; white-space:nowrap; letter-spacing:-1px; }}
.ctext {{ font-size:13px; line-height:1.45; color:{NAVY}; }}
.ctext b {{ font-weight:700; }}
"""

SOURCES = ("Sources : base IRVE (transport.data.gouv.fr), Agence ORE / AAA Data, "
           "geo.api.gouv.fr · données du 28/10/2026")
AUTEUR = "Célia Monga · github.com/sabcelia1/recharge-ve-france"


def page(titre, soustitre, corps, avec_region=True):
    region = (f'<div class="abs region-lbl">{icone("region", "blanc", 20)}Région</div>'
              f'<div class="abs slot-slicer"></div>') if avec_region else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body>
<div class="abs header"></div>
<div class="abs titre">{titre}</div>
<div class="abs soustitre">{soustitre}</div>
{region}
{corps}
<div class="abs footer"><span>{SOURCES}</span><span>{AUTEUR}</span></div>
</body></html>"""


def panel(x, y, w, h, titre="", sous=""):
    entete = (f'<div style="padding:16px 20px 0"><div class="ptitre">{titre}</div>'
              f'<div class="psous">{sous}</div></div>') if titre else ""
    return f'<div class="abs panel" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">{entete}</div>'


def callout(x, y, w, h, gros, texte):
    return (f'<div class="abs panel callout" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px">'
            f'<div class="big">{gros}</div><div class="ctext">{texte}</div></div>')


# Positions des visuels Power BI (x, y, largeur, hauteur) — page 1280 x 720
POSITIONS = {}

# --- Page 1 : vue d'ensemble ---------------------------------------------------------
KPI = [("borne", "Points de recharge", "ouverts au public"),
       ("voiture", "Véhicules électriques", "dernier trimestre disponible"),
       ("ratio", "VE par point", "tension sur le réseau public"),
       ("eclair", "Recharge rapide", "part des points de plus de 50 kW")]
corps1 = ""
for i, (ico, lbl, cap) in enumerate(KPI):
    x, y, w, h = 32 + i * 308, 96, 292, 116
    corps1 += (f'<div class="abs panel" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px"></div>'
               f'<div class="abs kpi-ico" style="left:{x+20}px;top:{y+32}px">{icone(ico, "vert", 28)}</div>'
               f'<div class="abs kpi-lbl" style="left:{x+82}px;top:{y+22}px;width:196px;text-align:center">{lbl}</div>'
               f'<div class="abs kpi-cap" style="left:{x+82}px;top:{y+94}px;width:196px;text-align:center">{cap}</div>')
    POSITIONS.setdefault("1 · Vue d'ensemble", []).append(
        (f"Carte « {lbl} »", x + 82, y + 36, 196, 56))
corps1 += panel(32, 228, 760, 460, "Parc de véhicules électriques et points de recharge",
                "France entière, par trimestre · points dont la date de mise en service est connue")
corps1 += panel(808, 228, 440, 460, "Points de recharge par puissance",
                "selon la région sélectionnée")
POSITIONS["1 · Vue d'ensemble"] += [
    ("Graphique d'évolution", 44, 282, 736, 396),
    ("Graphique par puissance", 820, 282, 416, 396),
    ("Segment Région", 1032, 20, 216, 36)]

# --- Page 2 : classement corrigé -------------------------------------------------------
corps2 = callout(32, 92, 1216, 64, "19 à 27",
                 "véhicules électriques par point dans le top 10 corrigé, contre <b>20 à 178</b> "
                 "avant correction : le classement brut mesurait surtout des <b>biais de données</b> "
                 "(outre-mer, flottes d'entreprise).")
corps2 += panel(32, 172, 500, 516, "Top 15 des départements les plus en tension",
                "véhicules électriques par point de recharge public")
corps2 += panel(548, 172, 700, 516, "Détail par département",
                "cliquer sur un en-tête de colonne pour trier")
POSITIONS["2 · Classement corrigé"] = [
    ("Graphique à barres (top 15)", 44, 226, 476, 450),
    ("Tableau des départements", 560, 226, 676, 450),
    ("Segment Région", 1032, 20, 216, 36)]

# --- Page 3 : déserts de recharge ------------------------------------------------------
corps3 = callout(32, 92, 1216, 64, "2,1",
                 "points de recharge pour 10 000 habitants à <b>Vitry-sur-Seine</b> (94 000 habitants), "
                 "<b>60 fois moins</b> qu'à Puteaux. La plupart des grandes communes les moins équipées "
                 "sont en <b>Île&#8209;de&#8209;France</b>, où les VE sont encore rares.")
corps3 += panel(32, 172, 500, 516, "Les 15 communes les moins équipées",
                "points de recharge pour 10 000 habitants · communes de plus de 30 000 habitants")
corps3 += panel(548, 172, 700, 516, "Équipement et adoption des VE",
                "chaque bulle est une commune (taille = population) · lignes = moyennes de la sélection")
POSITIONS["3 · Déserts de recharge"] = [
    ("Graphique à barres (15 communes)", 44, 226, 476, 450),
    ("Nuage de points", 560, 226, 676, 450),
    ("Segment Région", 1032, 20, 216, 36)]

# --- Page 4 : méthode (entièrement dessinée) -------------------------------------------
etapes = [("fichier", "Open data", "Bornes IRVE · immatriculations<br>par commune · référentiel INSEE"),
          ("code", "Python", "Nettoyage, rattachement GPS,<br>rapport de qualité"),
          ("base", "BigQuery", "Modèle en étoile,<br>vues SQL corrigées"),
          ("graphique", "Power BI", "Mesures DAX,<br>5 pages d'analyse")]
corps4 = '<div class="abs" style="left:32px;top:96px;font-size:12px;font-weight:700;color:#5B6676;letter-spacing:0.6px">CHAÎNE DE TRAITEMENT</div>'
for i, (ico, t, d) in enumerate(etapes):
    x = 32 + i * 308
    corps4 += (f'<div class="abs panel" style="left:{x}px;top:120px;width:276px;height:96px;'
               f'display:flex;align-items:center;gap:14px;padding:0 18px">'
               f'<div class="kpi-ico" style="flex:none">{icone(ico, "vert", 26)}</div>'
               f'<div><div class="ptitre">{t}</div><div class="psous" style="line-height:1.4">{d}</div></div></div>')
    if i < 3:
        corps4 += (f'<div class="abs" style="left:{x+280}px;top:156px;color:{TEAL};font-size:22px;'
                   f'font-weight:700">→</div>')


def colonne(x, titre, couleur, items):
    li = "".join(f'<li style="margin-bottom:10px">{t}</li>' for t in items)
    return (f'<div class="abs panel" style="left:{x}px;top:236px;width:392px;height:300px;padding:20px 24px">'
            f'<div style="height:4px;width:40px;background:{couleur};border-radius:2px;margin-bottom:14px"></div>'
            f'<div class="ptitre" style="font-size:16px;margin-bottom:14px">{titre}</div>'
            f'<ul style="font-size:12.5px;line-height:1.5;color:{NAVY};padding-left:18px">{li}</ul></div>')


corps4 += colonne(32, "Corrections appliquées", TEAL, [
    "<b>28 %</b> des points sans code commune exploitable, rattachés par leurs <b>coordonnées GPS</b>",
    "<b>Outre-mer</b> exclu des classements : couverture probablement incomplète des bornes déclarées",
    "<b>Communes « flottes »</b> exclues : plus de 2 voitures par habitant et au moins 1 000 voitures immatriculées (sièges d'entreprises, loueurs)",
    "Environ <b>2 700 points</b> sans puissance connue, exclus du graphique par puissance"])
corps4 += colonne(444, "Limites", AMBER, [
    "<b>47 %</b> des points n'ont pas de date de mise en service : la courbe d'évolution sous-estime le niveau mais montre la tendance",
    "Les flottes réparties dans de <b>grandes communes</b> ne sont pas détectables (ex. Hauts-de-Seine)",
    "La <b>recharge privée</b> (domicile, entreprise) n'est pas comptée",
    "Le rattachement GPS utilise le <b>centre de commune</b> le plus proche"])
corps4 += colonne(856, "Pour aller plus loin", NAVY, [
    "<b>Journal d'analyse</b> : 9 hypothèses formulées et testées une à une, y compris les pistes rejetées",
    "<b>Rapport de qualité</b> chiffré, régénéré à chaque exécution",
    "Piste d'extension : croiser avec les <b>revenus et le type de logement</b> (INSEE) pour expliquer les déserts de recharge",
    "Code, SQL et documentation :<br><b>github.com/sabcelia1/recharge-ve-france</b>"])

RESULTATS = [("99,96 %", "des points de recharge rattachés à une commune, dont 28 % grâce au GPS"),
             ("19 à 27", "VE par point dans le top 10 corrigé, contre 20 à 178 avant correction"),
             ("× 60", "d'écart de densité de bornes entre Vitry-sur-Seine et Puteaux")]
corps4 += ('<div class="abs" style="left:32px;top:556px;font-size:12px;font-weight:700;color:#5B6676;'
           'letter-spacing:0.6px">PRINCIPAUX RÉSULTATS</div>')
for i, (chiffre, texte) in enumerate(RESULTATS):
    x = 32 + i * 412
    corps4 += (f'<div class="abs panel callout" style="left:{x}px;top:580px;width:392px;height:104px">'
               f'<div class="big" style="font-size:30px">{chiffre}</div>'
               f'<div class="ctext" style="font-size:12.5px">{texte}</div></div>')

# --- Page 5 : opportunités d'implantation ----------------------------------------------
corps5 = ""
CHIFFRES = [("100", "grandes communes où la <b>demande n'est pas servie</b> : moins de bornes que la médiane et plus de VE par point"),
            ("6 354", "points manquants pour atteindre la <b>densité médiane</b> (21,2 points pour 10 000 habitants)"),
            ("13 à 32 M€", "pour les installer en <b>recharge normale</b> (2 000 à 5 000 € par point, 7 à 22 kW)")]
for i, (chiffre, texte) in enumerate(CHIFFRES):
    x = 32 + i * 411
    corps5 += (f'<div class="abs panel callout" style="left:{x}px;top:92px;width:394px;height:76px;gap:16px;padding:0 20px">'
               f'<div class="big" style="font-size:28px">{chiffre}</div>'
               f'<div class="ctext" style="font-size:12px;line-height:1.4">{texte}</div></div>')

AXES = [("1", TEAL, "Petite couronne parisienne", "15 communes · 1 669 points manquants · ≈ 3 à 8 M€",
         "Vitry-sur-Seine, Saint-Denis, Argenteuil, Colombes… Les rares bornes sont <b>déjà saturées</b> "
         "(jusqu'à 94 VE par point à Maisons-Alfort). <b>Recharge normale</b> sur voirie et parkings publics, "
         "pour les habitants sans parking privé."),
        ("2", NAVY, "Métropole de Lyon", "Lyon, Villeurbanne · 816 points manquants · ≈ 1,6 à 4 M€",
         "Lyon compte <b>10 points pour 10 000 habitants</b>, deux fois moins que la médiane : le plus gros "
         "déficit d'une seule commune (570 points). Recharge normale en quartier, et quelques <b>hubs rapides</b>."),
        ("3", AMBER, "Grandes villes de province", "6 villes · 943 points manquants · ≈ 1,9 à 4,7 M€",
         "Marseille, Nantes, Orléans, Le Mans, Reims, Dunkerque : déficit réel mais <b>tension modérée</b> "
         "(16 à 29 VE par point). Priorité 2, à <b>planifier avec les collectivités</b>.")]
for i, (num, col, titre, chiffres, texte) in enumerate(AXES):
    y = 184 + i * 156
    corps5 += (f'<div class="abs panel" style="left:{x0}px;top:{y}px;width:600px;height:144px;padding:16px 20px 0 76px">'.format() if False else
               f'<div class="abs panel" style="left:32px;top:{y}px;width:600px;height:144px;padding:16px 22px 0 78px">'
               f'<div class="abs" style="left:20px;top:18px;width:40px;height:40px;border-radius:50%;background:{col};'
               f'color:#fff;font-size:18px;font-weight:800;display:flex;align-items:center;justify-content:center">{num}</div>'
               f'<div class="ptitre" style="font-size:15px">{titre}</div>'
               f'<div style="font-size:11.5px;font-weight:700;color:{TEAL if col != AMBER else "#C47F12"};margin:3px 0 8px">{chiffres}</div>'
               f'<div style="font-size:12px;line-height:1.45;color:{NAVY}">{texte}</div></div>')
corps5 += panel(648, 184, 600, 456, "Communes prioritaires",
                "profil « demande non servie » · triées par points manquants")
corps5 += ('<div class="abs" style="left:32px;top:652px;width:1216px;font-size:10.5px;line-height:1.45;color:#5B6676">'
           '<b>À confirmer sur le terrain.</b> Demande mesurée par les immatriculations, sans données d\'usage ; la base IRVE compte '
           'environ 12 % de points de moins que le baromètre Avere-France, donc le déficit est probablement surestimé ; coûts : ordres de '
           'grandeur relevés dans la presse (Économie Matin, 24/10/2026). Analyse exploratoire, pas une recommandation d\'investissement.</div>')
POSITIONS["5 · Opportunités"] = [
    ("Tableau des communes prioritaires", 660, 238, 576, 392),
    ("Segment Région", 1032, 20, 216, 36)]

PAGES = {
    "1_vue_ensemble": page("Recharge électrique en France", "Vue d'ensemble · bornes publiques et parc de véhicules électriques", corps1),
    "2_classement_corrige": page("Classement corrigé des départements", "Métropole · communes à suspicion de flotte exclues", corps2),
    "3_deserts_recharge": page("Les déserts de recharge", "Communes de plus de 30 000 habitants · métropole, hors flottes", corps3),
    "5_opportunites": page("Opportunités d'implantation", "Où installer des points de recharge en priorité ? · communes de plus de 30 000 habitants, métropole, hors flottes", corps5),
    "4_methode_limites": page("Méthode et limites", "D'où viennent les chiffres, ce qui a été corrigé, ce qui reste incertain", corps4, avec_region=False),
}

if __name__ == "__main__":
    out = ICI / "html"
    out.mkdir(exist_ok=True)
    for nom, html in PAGES.items():
        (out / f"{nom}.html").write_text(html, encoding="utf-8")
    (ICI / "positions.json").write_text(json.dumps(POSITIONS, indent=2, ensure_ascii=False), encoding="utf-8")
    print("ok :", ", ".join(PAGES))
