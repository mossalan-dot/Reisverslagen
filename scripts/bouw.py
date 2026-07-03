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
from datetime import date
from pathlib import Path

import yaml

WORTEL = Path(__file__).resolve().parent.parent
DATA = WORTEL / "data"
DOCS = WORTEL / "docs"
ID_PATROON = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PREVIEW = 280

fouten, waarschuwingen = [], []


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

    def schoon(records):
        return [{k: v for k, v in r.items() if k != "_bestand"} for r in records]

    vol = {
        "gegenereerd": date.today().isoformat(),
        "reizigers": schoon(reizigers), "reizen": schoon(reizen),
        "manuscripten": schoon(manuscripten), "instellingen": schoon(instellingen),
    }
    DOCS.mkdir(exist_ok=True)
    (DOCS / "data.json").write_text(json.dumps(vol, ensure_ascii=False), encoding="utf-8")

    # lichte versie: lange teksten inkorten (worden nageladen uit data.json)
    licht = copy.deepcopy(vol)
    ingekort = 0
    for reis in licht["reizen"]:
        for sleutel in ("brieven", "poezie"):
            for item in reis.get(sleutel, []):
                t = item.get("tekst") or ""
                if len(t) > PREVIEW:
                    item["tekst"] = t[:PREVIEW].rstrip() + "…"
                    item["_ingekort"] = True
                    ingekort += 1
    sjabloon = (WORTEL / "scripts" / "sjabloon.html").read_text(encoding="utf-8")
    html = sjabloon.replace("__DATA_JSON__", json.dumps(licht, ensure_ascii=False))
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    kb = (DOCS / "index.html").stat().st_size // 1024
    print(f"Website gebouwd: index.html ({kb} KB, {ingekort} teksten ingekort), data.json volledig.")


if __name__ == "__main__":
    hoofd()
