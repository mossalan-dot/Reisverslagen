#!/usr/bin/env python3
"""Leest de bibliografie uit het Apple Pages-bestand (biblio.pages) en schrijft
data/bibliografie.yaml: de volledige titels van de corpusverslagen (per P.No.)
en een verwijzingenregister (korte verwijzing 'Auteur jaar' -> volledige titel).

Gebruik:
    python3 scripts/extract_bibliografie.py <biblio.pages>

Het Pages-bestand zelf hoort niet in de repository; het resultaat
(data/bibliografie.yaml) wel.
"""

import re
import sys
import unicodedata
import zipfile
from pathlib import Path

import cramjam
import yaml

WORTEL = Path(__file__).resolve().parent.parent


def pages_tekst(pad):
    with zipfile.ZipFile(pad) as z:
        raw = z.read("Index/Document.iwa")
    out = bytearray()
    i = 0
    while i + 4 <= len(raw):
        ln = int.from_bytes(raw[i + 1:i + 4], "little")
        i += 4
        blok = raw[i:i + ln]
        i += ln
        try:
            out += bytes(cramjam.snappy.decompress_raw(blok))
        except Exception:
            pass
    s = bytes(out).decode("utf-8", "replace")
    runs = re.findall(r"[^\x00-\x08\x0e-\x1f�]{30,}", s)
    return max(runs, key=len)


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z]", "", s.lower())


PARTIKELS = {"van", "de", "der", "den", "het", "ten", "ter", "von", "la", "le",
             "du", "di", "del", "della"}


def surnames_van_entry(entry):
    """Plausibele achternamen (van de eerste auteur) om op te indexeren:
    de volledige achternaam plus het laatste niet-tussenvoegsel-woord."""
    eerste = entry.split(".")[0].split(",")[0].strip()
    namen = {norm(eerste)}
    woorden = [w for w in re.split(r"[-\s]+", eerste) if norm(w) and norm(w) not in PARTIKELS]
    if woorden:
        namen.add(norm(woorden[-1]))
    return {n for n in namen if len(n) > 2}


def hoofd():
    if len(sys.argv) < 2:
        sys.exit("gebruik: python3 scripts/extract_bibliografie.py <biblio.pages>")
    run = pages_tekst(sys.argv[1])

    titels = {"1.2.1": "Reisverslagen binnen", "1.2.2": "Reisverslagen buiten",
              "1.2.3": "Reisverslagen in editie", "1.2.4": "Reisliteratuur in druk",
              "1.3": "Correspondentie", "1.4": "Overige handschriftelijke",
              "1.5": "Gedrukte bronnen voor 1850", "1.6": "Online repertoria",
              "1.7": "Secundaire literatuur"}
    pos = {}
    for k, t in titels.items():
        m = re.search(re.escape(k) + r"\.?\s+" + re.escape(t), run)
        pos[k] = m.start() if m else run.index(k)

    # --- 1.2.1 corpusverslagen: P.No. -> volledige titel ---
    corpus = {}
    seg = run[pos["1.2.1"]:pos["1.2.2"]]
    for regel in seg.split("\n"):
        m = re.search(r"\[P\.\s*No\.\s*([\d\s,-]+)\]", regel)
        if not m:
            continue
        titel = regel[:m.start()].strip().rstrip(".") + "."
        nummers = []
        for stuk in re.split(r"[,\s]+", m.group(1).strip()):
            mm = re.match(r"(\d+)(?:-(\d+))?$", stuk)
            if mm:
                a = int(mm.group(1)); b = int(mm.group(2) or a)
                nummers += [f"{n:03d}" for n in range(a, b + 1)]
        for n in nummers:
            corpus[n] = titel

    # --- verwijzingenregister uit alle auteur-jaar-secties (primair + secundair) ---
    secties = [("1.2.1", "1.2.2"), ("1.2.2", "1.2.3"), ("1.2.3", "1.2.4"),
               ("1.2.4", "1.3"), ("1.3", "1.4"), ("1.4", "1.5"),
               ("1.5", "1.6"), ("1.6", "1.7"), ("1.7", None)]
    register = {}   # 'achternaam jaar[suffix]' -> volledige titel
    per_naamjaar = {}  # (surname,jaar) -> [citaties] om a/b toe te kennen
    for a, b in secties:
        seg = run[pos[a]:(pos[b] if b else len(run))]
        regels = [r.strip() for r in seg.split("\n") if len(r.strip()) > 12][1:]
        for entry in regels:
            # indexeer op elk jaartal in de entry (publicatiejaar staat niet altijd achteraan)
            for jaar in set(re.findall(r"\b(1[4-9]\d\d|20\d\d)\b", entry)):
                for sn in surnames_van_entry(entry):
                    per_naamjaar.setdefault((sn, jaar), [])
                    if entry not in per_naamjaar[(sn, jaar)]:
                        per_naamjaar[(sn, jaar)].append(entry)

    for (sn, jaar), lijst in per_naamjaar.items():
        register[f"{sn} {jaar}"] = lijst[0]
        if len(lijst) > 1:
            for k, cit in enumerate(lijst):
                register[f"{sn} {jaar}{chr(ord('a') + k)}"] = cit

    data = {"corpus": corpus, "verwijzingen": register}
    pad = WORTEL / "data" / "bibliografie.yaml"
    pad.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=True, width=200),
                   encoding="utf-8")
    print(f"Geschreven: {len(corpus)} corpustitels, {len(register)} verwijzingssleutels "
          f"({pad.relative_to(WORTEL)}).")


if __name__ == "__main__":
    hoofd()
