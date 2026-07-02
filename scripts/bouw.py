#!/usr/bin/env python3
"""Controleert de gegevens in data/ en bouwt de website in docs/.

Gebruik:
    python3 scripts/bouw.py            controleer en bouw
    python3 scripts/bouw.py --controle alleen controleren, niets bouwen
"""

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

REISTYPEN = {
    "educatiereis", "pelgrimsreis", "diplomatieke reis", "handelsreis",
    "militaire reis", "plezierreis", "gemengd", "overig", "onbekend",
}
MANUSCRIPTTYPEN = {"klad", "net", "kopie", "brieven", "overig", "onbekend"}
STATUSSEN = {"geen", "gedeeltelijk", "volledig", "onbekend"}
INSTELLINGSTYPEN = {"archief", "bibliotheek", "museum", "particulier", "overig"}

fouten = []
waarschuwingen = []


def laad_map(naam):
    """Laadt alle YAML-bestanden uit data/<naam>/ en controleert de id's."""
    records = []
    map_ = DATA / naam
    if not map_.is_dir():
        return records
    for pad in sorted(map_.glob("*.yaml")) + sorted(map_.glob("*.yml")):
        rel = pad.relative_to(WORTEL)
        try:
            record = yaml.safe_load(pad.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            fouten.append(f"{rel}: YAML-fout: {e}")
            continue
        if not isinstance(record, dict):
            fouten.append(f"{rel}: bestand bevat geen veldenlijst")
            continue
        record["_bestand"] = str(rel)
        records.append(record)
    return records


def controleer(records, soort, verplicht):
    ids = set()
    for r in records:
        rel = r["_bestand"]
        rid = r.get("id")
        if not rid or not isinstance(rid, str) or not ID_PATROON.match(rid):
            fouten.append(f"{rel}: ontbrekende of ongeldige id (kleine letters, cijfers, koppeltekens)")
            continue
        if rid in ids:
            fouten.append(f"{rel}: dubbele id '{rid}'")
        ids.add(rid)
        for veld in verplicht:
            if not r.get(veld):
                fouten.append(f"{rel}: verplicht veld '{veld}' ontbreekt of is leeg")
    return ids


def controleer_verwijzingen(records, veld, doel_ids, doelnaam, lijst=True):
    for r in records:
        waarde = r.get(veld)
        if not waarde:
            continue
        verwijzingen = waarde if lijst else [waarde]
        for v in verwijzingen:
            if v not in doel_ids:
                fouten.append(f"{r['_bestand']}: '{veld}' verwijst naar onbekende {doelnaam} '{v}'")


def controleer_keuze(records, veld, toegestaan, subveld=None):
    for r in records:
        waarde = r.get(veld)
        if subveld and isinstance(waarde, dict):
            waarde = waarde.get(subveld)
        if waarde and waarde not in toegestaan:
            plek = f"{veld}.{subveld}" if subveld else veld
            fouten.append(
                f"{r['_bestand']}: '{plek}' heeft ongeldige waarde '{waarde}' "
                f"(toegestaan: {', '.join(sorted(toegestaan))})"
            )


def hoofd():
    alleen_controle = "--controle" in sys.argv[1:]

    reizigers = laad_map("reizigers")
    reizen = laad_map("reizen")
    manuscripten = laad_map("manuscripten")
    instellingen = laad_map("instellingen")

    reiziger_ids = controleer(reizigers, "reiziger", ["naam"])
    reis_ids = controleer(reizen, "reis", ["titel", "reizigers"])
    manuscript_ids = controleer(manuscripten, "manuscript", ["titel_aanduiding"])
    instelling_ids = controleer(instellingen, "instelling", ["naam"])

    # Controleer dat id's over alle soorten heen uniek zijn.
    alle = {}
    for soort, ids in [("reiziger", reiziger_ids), ("reis", reis_ids),
                       ("manuscript", manuscript_ids), ("instelling", instelling_ids)]:
        for rid in ids:
            if rid in alle:
                fouten.append(f"id '{rid}' komt voor als {alle[rid]} én als {soort}")
            alle[rid] = soort

    controleer_verwijzingen(reizen, "reizigers", reiziger_ids, "reiziger")
    controleer_verwijzingen(manuscripten, "reizen", reis_ids, "reis")
    controleer_verwijzingen(manuscripten, "auteurs", reiziger_ids, "reiziger")
    controleer_verwijzingen(manuscripten, "instelling", instelling_ids, "instelling", lijst=False)

    controleer_keuze(reizen, "reistype", REISTYPEN)
    controleer_keuze(manuscripten, "manuscripttype", MANUSCRIPTTYPEN)
    controleer_keuze(manuscripten, "digitalisering", STATUSSEN, subveld="status")
    controleer_keuze(manuscripten, "transcriptie", STATUSSEN, subveld="status")
    controleer_keuze(instellingen, "type", INSTELLINGSTYPEN)

    for m in manuscripten:
        if not m.get("instelling"):
            waarschuwingen.append(f"{m['_bestand']}: geen bewaarinstelling opgegeven")

    te_controleren = sum(
        1 for r in reizigers + reizen + manuscripten + instellingen if r.get("controle_nodig")
    )

    if fouten:
        print(f"FOUTEN ({len(fouten)}):")
        for f in fouten:
            print(f"  - {f}")
    if waarschuwingen:
        print(f"Waarschuwingen ({len(waarschuwingen)}):")
        for w in waarschuwingen:
            print(f"  - {w}")
    print(
        f"Gelezen: {len(reizigers)} reizigers, {len(reizen)} reizen, "
        f"{len(manuscripten)} manuscripten, {len(instellingen)} instellingen "
        f"({te_controleren} records gemarkeerd met controle_nodig)."
    )
    if fouten:
        sys.exit(1)
    if alleen_controle:
        print("Controle geslaagd.")
        return

    def schoon(records):
        return [{k: v for k, v in r.items() if k != "_bestand"} for r in records]

    dataset = {
        "gegenereerd": date.today().isoformat(),
        "reizigers": schoon(reizigers),
        "reizen": schoon(reizen),
        "manuscripten": schoon(manuscripten),
        "instellingen": schoon(instellingen),
    }

    DOCS.mkdir(exist_ok=True)
    (DOCS / "data.json").write_text(
        json.dumps(dataset, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    sjabloon = (WORTEL / "scripts" / "sjabloon.html").read_text(encoding="utf-8")
    html = sjabloon.replace("__DATA_JSON__", json.dumps(dataset, ensure_ascii=False))
    (DOCS / "index.html").write_text(html, encoding="utf-8")
    print(f"Website gebouwd: {DOCS / 'index.html'}")


if __name__ == "__main__":
    hoofd()
