#!/usr/bin/env python3
"""Controleert de gegevens in data/ en bouwt de website in docs/.

Gebruik:
    python3 scripts/bouw.py            controleer en bouw
    python3 scripts/bouw.py --controle alleen controleren, niets bouwen

De volledige dataset komt in docs/data.json. In docs/index.html wordt een
lichte versie ingebed (zonder de lange brief- en gedichtteksten); die worden
bij het openen van een detail nageladen uit data.json.
"""

import copy
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

import yaml

WORTEL = Path(__file__).resolve().parent.parent
DATA = WORTEL / "data"
DOCS = WORTEL / "docs"
ID_PATROON = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PREVIEW = 280
PARTIKELS = {"van", "de", "der", "den", "het", "ten", "ter", "von", "la", "le",
             "du", "di", "del", "della"}

fouten, waarschuwingen = [], []


def _norm(s):
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())


def laad_bibliografie():
    pad = DATA / "bibliografie.yaml"
    if not pad.is_file():
        return {}, {}
    b = yaml.safe_load(pad.read_text(encoding="utf-8")) or {}
    return b.get("corpus", {}) or {}, b.get("verwijzingen", {}) or {}


def resolveer(tekst, register):
    """Zoekt in één literatuurregel de korte verwijzingen op in het register.
    Geeft (aantal_refs, [volledige titels]) terug; alleen zekere (unieke
    achternaam+jaar) treffers worden gekoppeld."""
    gevonden = []
    n_ref = 0
    for stuk in re.split(r";\s*", str(tekst)):
        m = re.match(r"^([A-ZÀ-Ý][A-Za-zÀ-ÿ'’.\- ]+?)\s+(1[4-9]\d\d|20\d\d)([a-z])?\b",
                     stuk.strip())
        if not m:
            continue
        n_ref += 1
        woorden = m.group(1).split()
        while len(woorden) > 1 and _norm(woorden[0]) in PARTIKELS:
            woorden = woorden[1:]
        sleutel = f"{_norm(''.join(woorden))} {m.group(2)}{m.group(3) or ''}"
        kaal = f"{_norm(''.join(woorden))} {m.group(2)}"
        titel = register.get(sleutel) or register.get(kaal)
        if titel and titel not in gevonden:
            gevonden.append(titel)
    return n_ref, gevonden


def laad_map(naam):
    records = []
    map_ = DATA / naam
    if not map_.is_dir():
        return records
    for pad in sorted(map_.glob("*.yaml")):
        rel = pad.relative_to(WORTEL)
        try:
            r = yaml.safe_load(pad.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            fouten.append(f"{rel}: YAML-fout: {e}")
            continue
        if not isinstance(r, dict):
            fouten.append(f"{rel}: geen veldenlijst")
            continue
        r["_bestand"] = str(rel)
        records.append(r)
    return records


def controleer(records, verplicht):
    ids = set()
    for r in records:
        rid = r.get("id")
        if not rid or not ID_PATROON.match(str(rid)):
            fouten.append(f"{r['_bestand']}: ontbrekende of ongeldige id")
            continue
        if rid in ids:
            fouten.append(f"{r['_bestand']}: dubbele id '{rid}'")
        ids.add(rid)
        for veld in verplicht:
            if not r.get(veld):
                fouten.append(f"{r['_bestand']}: verplicht veld '{veld}' ontbreekt")
    return ids


def verwijzing(records, veld, doel, naam, lijst=True):
    for r in records:
        w = r.get(veld)
        if not w:
            continue
        for v in (w if lijst else [w]):
            if v not in doel:
                fouten.append(f"{r['_bestand']}: '{veld}' verwijst naar onbekende {naam} '{v}'")


def hoofd():
    alleen = "--controle" in sys.argv[1:]
    reizigers = laad_map("reizigers")
    reizen = laad_map("reizen")
    manuscripten = laad_map("manuscripten")
    instellingen = laad_map("instellingen")

    r_ids = controleer(reizigers, ["naam"])
    reis_ids = controleer(reizen, ["titel"])
    m_ids = controleer(manuscripten, ["titel_aanduiding"])
    i_ids = controleer(instellingen, ["naam"])

    verwijzing(reizen, "reizigers", r_ids, "reiziger")
    verwijzing(reizen, "manuscript", m_ids, "manuscript", lijst=False)
    verwijzing(manuscripten, "reizen", reis_ids, "reis")
    verwijzing(manuscripten, "auteurs", r_ids, "reiziger")
    verwijzing(manuscripten, "instelling", i_ids, "instelling", lijst=False)

    for m in manuscripten:
        if not m.get("instelling"):
            waarschuwingen.append(f"{m['_bestand']}: geen bewaarinstelling")

    if fouten:
        print(f"FOUTEN ({len(fouten)}):")
        for f in fouten[:40]:
            print("  -", f)
    if waarschuwingen:
        print(f"Waarschuwingen: {len(waarschuwingen)}")
    print(f"Gelezen: {len(reizigers)} reizigers, {len(reizen)} reizen, "
          f"{len(manuscripten)} manuscripten, {len(instellingen)} instellingen.")
    if fouten:
        sys.exit(1)
    if alleen:
        print("Controle geslaagd.")
        return

    # bibliografie koppelen (bij het bouwen, zonder de databestanden te wijzigen)
    corpus, register = laad_bibliografie()
    n_titel = n_ref_tot = n_ref_ok = 0
    for m in manuscripten:
        c = m.get("corpus_gor")
        if c and str(c).zfill(3) in corpus:
            m["formele_titel"] = corpus[str(c).zfill(3)]
            n_titel += 1
    for records in (reizigers, reizen, manuscripten):
        for r in records:
            vol_titels = []
            for veld in ("literatuur", "edities"):
                for lit in (r.get(veld) or []):
                    n, gevonden = resolveer(lit, register)
                    n_ref_tot += n
                    for g in gevonden:
                        if g not in vol_titels:
                            vol_titels.append(g)
            n_ref_ok += len(vol_titels)
            if vol_titels:
                r["literatuur_volledig"] = vol_titels
    print(f"Bibliografie: {n_titel} manuscripttitels gekoppeld; "
          f"{n_ref_ok} van {n_ref_tot} literatuurverwijzingen aan een volledige titel gekoppeld.")

    # verrijkingen platslaan tot eigen doorzoekbare secties (met verwijzing terug)
    brieven, gedichten, addenda, portretten = [], [], [], []
    for reis in reizen:
        basis = {"reis": reis["id"], "reizigers": reis.get("reizigers") or []}
        for i, b in enumerate(reis.get("brieven") or []):
            brieven.append({**b, "id": f"{reis['id']}-brief-{i + 1}", **basis})
        for i, p in enumerate(reis.get("poezie") or []):
            gedichten.append({**p, "id": f"{reis['id']}-gedicht-{i + 1}", **basis})
        for i, a in enumerate(reis.get("addenda") or []):
            addenda.append({**a, "id": f"{reis['id']}-addendum-{i + 1}", **basis})
    for rz in reizigers:
        for i, p in enumerate(rz.get("portretten") or []):
            portretten.append({**p, "id": f"{rz['id']}-portret-{i + 1}", "reiziger": rz["id"]})

    def schoon(records, drop=()):
        return [{k: v for k, v in r.items() if k != "_bestand" and k not in drop}
                for r in records]

    vol = {
        "gegenereerd": date.today().isoformat(),
        "reizigers": schoon(reizigers, {"portretten"}),
        "reizen": schoon(reizen, {"brieven", "poezie", "addenda"}),
        "manuscripten": schoon(manuscripten), "instellingen": schoon(instellingen),
        "brieven": brieven, "gedichten": gedichten, "addenda": addenda, "portretten": portretten,
    }
    print(f"Secties: {len(brieven)} brieven, {len(gedichten)} gedichten, "
          f"{len(addenda)} addenda, {len(portretten)} portretten.")
    DOCS.mkdir(exist_ok=True)
    (DOCS / "data.json").write_text(json.dumps(vol, ensure_ascii=False), encoding="utf-8")

    # lichte versie: lange teksten inkorten (worden nageladen uit data.json)
    licht = copy.deepcopy(vol)
    ingekort = 0
    for sleutel in ("brieven", "gedichten"):
        for item in licht[sleutel]:
            t = item.get("tekst") or ""
            if len(t) > PREVIEW:
                item["tekst"] = t[:PREVIEW].rstrip() + "…"
                item["_ingekort"] = True
                ingekort += 1
    sjabloon = (WORTEL / "scripts" / "sjabloon.html").read_text(encoding="utf-8")
    html = sjabloon.replace("__DATA_JSON__", json.dumps(licht, ensure_ascii=False))
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    kb = (DOCS / "index.html").stat().st_size // 1024
    schrijf_zoekhulp()
    print(f"Website gebouwd: index.html ({kb} KB, {ingekort} teksten ingekort), "
          f"data.json en zoekhulp.html.")


# Zoektermen die in archiefinventarissen vaak op handgeschreven reisverslagen wijzen.
ZOEKTERMEN = [
    "reisjournaal", "reisverslag", "reisdagboek", "reisverhaal", "reisbeschrijving",
    '"journael van mijn reijse"', "journael reijse", '"reyse naer"', '"reijse door"',
    "itinerarium", '"dagverhael van mijn reise"', '"beschrijvinge van mijn reijse"',
    "educatiereis", "grand tour reisverslag", '"reijse naar Italien"',
    '"reijse door Vranckrijck"', '"voyage" journael handschrift',
]
STAANDE_BRONNEN = [
    ("Repertorium reisverslagen (Lindeman, Scherf en Dekker)", "http://www.egodocument.net/reisverslagen.html"),
    ("Egodocumenten — reisverslagen 1500–1814", "https://www.egodocumenten.nl/reisverslagen-van-1500-1814/"),
    ("A. Frank-van Westrienen, De groote tour (handschriftenlijst, DBNL)",
     "https://www.dbnl.org/tekst/fran014groo01_01/fran014groo01_01_0013.php"),
    ("Bijzondere Collecties UB Leiden — handschriften", "https://www.bibliotheek.universiteitleiden.nl/bijzondere-collecties"),
    ("Special Collections UB Utrecht — manuscripts", "https://www.uu.nl/en/special-collections/collections/manuscripts"),
]


def schrijf_zoekhulp():
    from urllib.parse import quote_plus

    def links(term):
        q = quote_plus(term)
        cat = [
            ("archieven.nl", f"https://www.archieven.nl/nl/zoeken?mivast=0&miview=tbl&milang=nl&mizk_alle={q}"),
            ("WorldCat", f"https://search.worldcat.org/search?q={q}"),
            ("Nationaal Archief", f"https://www.google.com/search?q=site%3Anationaalarchief.nl+{q}"),
            ("Google Boeken", f"https://www.google.com/search?tbm=bks&q={q}"),
        ]
        return " · ".join(f'<a href="{u}" target="_blank" rel="noopener">{n}</a>' for n, u in cat)

    rijen = "".join(
        f'<tr><td class="term">{t}</td><td>{links(t)}</td></tr>' for t in ZOEKTERMEN)
    bronnen = "".join(
        f'<li><a href="{u}" target="_blank" rel="noopener">{n}</a></li>' for n, u in STAANDE_BRONNEN)
    pagina = f"""<!DOCTYPE html><html lang="nl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Zoekhulp — nieuwe reisverslagen vinden</title>
<style>
 body{{margin:0;background:#faf7f1;color:#2b2620;font:16px/1.55 Georgia,serif;}}
 header{{background:#2b2620;color:#f3efe7;padding:1.4rem 1rem;}}
 .kolom{{max-width:60rem;margin:0 auto;padding:0 1rem;}}
 h1{{margin:0;font-size:1.5rem;font-weight:normal;}} h2{{font-weight:normal;color:#7a2e2e;}}
 a{{color:#7a2e2e;}} p{{max-width:44rem;}}
 table{{border-collapse:collapse;width:100%;margin:1rem 0;font-size:.95rem;}}
 td{{border-bottom:1px solid #e3dcd0;padding:.5rem .4rem;vertical-align:top;}}
 td.term{{font-family:system-ui,sans-serif;font-size:.9rem;white-space:nowrap;color:#2b2620;}}
 .terug{{display:inline-block;margin:1rem 0;}}
</style></head><body>
<header><div class="kolom"><h1>Zoekhulp — nieuwe reisverslagen vinden</h1></div></header>
<main class="kolom">
<p><a class="terug" href="index.html">← terug naar het compendium</a></p>
<p>Deze pagina helpt bij het opsporen van handgeschreven reisverslagen die <em>nog niet</em>
in het compendium staan. Per zoekterm staan kant-en-klare zoekopdrachten in de belangrijkste
catalogi. Controleer een vondst altijd, en voeg hem toe via de bewerkmodus op de recordpagina's.</p>
<h2>Zoektermen × catalogi</h2>
<table><tbody>{rijen}</tbody></table>
<h2>Staande bronnen en repertoria</h2>
<ul>{bronnen}</ul>
<p style="color:#7a715f;font-size:.9rem;">Tip: de meeste onontdekte verslagen zitten in
archiefinventarissen (familie- en huisarchieven) op archieven.nl en nationaalarchief.nl.
Zoek daar ook op familienamen van bekende reizigersgeslachten.</p>
</main></body></html>"""
    (DOCS / "zoekhulp.html").write_text(pagina, encoding="utf-8")


if __name__ == "__main__":
    hoofd()
