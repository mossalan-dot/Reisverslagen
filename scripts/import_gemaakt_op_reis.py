#!/usr/bin/env python3
"""Importeert appendix A (Reizigers) en B (Reisverslagen) uit het Mellel-
bronbestand van Alan Moss, 'Gemaakt op reis' (2022) en schrijft ze als
YAML-records naar data/.

Gebruik:
    python3 scripts/import_gemaakt_op_reis.py <pad naar main.xml>

Het Mellel-bestand zelf maakt geen deel uit van deze repository. Het script
is idempotent: bestaande records met dezelfde id worden overschreven.
"""

import re
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path

import yaml

WORTEL = Path(__file__).resolve().parent.parent
DATA = WORTEL / "data"

LABEL_RE = re.compile(
    r"^(Reizen|Verslagen|Verslag|Addenda|Correspondentie|Poëzie|Literatuur|"
    r"Editie|Edities|Transcriptie|Transcripties):\s*(.*)$", re.S)
JAARKOP_RE = re.compile(r"^(?:[Cc]a\.\s*)?\d{4}(?:[-/]\d{2,4})?(?:\s+[IVX]+)?$")
DATUM_DEEL = r"(?:ca\.\s*)?(?:\d{1,2}\s+\w+\s+)?\d{4}"

LANDEN = {"NL": "Nederland", "FR": "Frankrijk", "IT": "Italië", "ZW": "Zwitserland",
          "SP": "Spanje", "EN": "Engeland", "ZN": "België", "DU": "Duitsland",
          "PO": "Portugal", "SU": "Suriname"}
DOEL_NAAR_REISTYPE = {"Educatie": "educatiereis", "Cultuur/vermaak": "plezierreis",
                      "Cultuur": "plezierreis", "Vermaak": "plezierreis",
                      "Zaken": "handelsreis", "Diplomatie": "diplomatieke reis",
                      "Militair": "militaire reis", "Religie": "pelgrimsreis",
                      "Anders": "overig"}
REISTYPE_TITEL = {"educatiereis": "Educatiereis", "plezierreis": "Plezierreis",
                  "handelsreis": "Zakenreis", "diplomatieke reis": "Diplomatieke reis",
                  "militaire reis": "Militaire reis", "pelgrimsreis": "Pelgrimsreis",
                  "overig": "Reis", "onbekend": "Reis"}
RELIGIES = ("Katholiek", "Gereformeerd", "Remonstrants", "Contraremonstrants",
            "Doopsgezind", "Luthers", "Waals", "Anglicaans", "Joods", "Protestants")

# Bekende bewaarinstellingen: afkorting (met plaats) -> record.
INSTELLINGEN = {
    ("Den Haag", "KB"): dict(id="kb-nationale-bibliotheek", naam="KB, nationale bibliotheek",
                             plaats="Den Haag", type="bibliotheek", website="https://www.kb.nl"),
    ("Amsterdam", "UBA"): dict(id="allard-pierson", naam="Allard Pierson (Universiteit van Amsterdam)",
                               plaats="Amsterdam", type="bibliotheek", website="https://allardpierson.nl",
                               opmerkingen="Erfgoedinstelling van de Universiteit van Amsterdam; omvat de "
                                           "Bijzondere Collecties van de voormalige Universiteitsbibliotheek "
                                           "Amsterdam (UBA)."),
    ("Leeuwarden", "Tresoar"): dict(id="tresoar", naam="Tresoar", plaats="Leeuwarden",
                                    type="archief", website="https://www.tresoar.nl"),
    ("Den Haag", "NA"): dict(id="nationaal-archief", naam="Nationaal Archief", plaats="Den Haag",
                             type="archief", website="https://www.nationaalarchief.nl",
                             opmerkingen="Tot 2002 Algemeen Rijksarchief (ARA)."),
    ("Middelburg", "ZA"): dict(id="zeeuws-archief", naam="Zeeuws Archief", plaats="Middelburg",
                               type="archief", website="https://www.zeeuwsarchief.nl"),
    ("Leiden", "UBL"): dict(id="ub-leiden", naam="Universitaire Bibliotheken Leiden",
                            plaats="Leiden", type="bibliotheek",
                            website="https://www.bibliotheek.universiteitleiden.nl"),
    ("Den Haag", "HRvA"): dict(id="hoge-raad-van-adel", naam="Hoge Raad van Adel", plaats="Den Haag",
                               type="overig", website="https://www.hogeraadvanadel.nl"),
    ("Antwerpen", "MPM"): dict(id="museum-plantin-moretus", naam="Museum Plantin-Moretus",
                               plaats="Antwerpen", land="België", type="museum",
                               website="https://museumplantinmoretus.be"),
    ("Utrecht", "UA"): dict(id="het-utrechts-archief", naam="Het Utrechts Archief", plaats="Utrecht",
                            type="archief", website="https://hetutrechtsarchief.nl"),
    ("Amsterdam", "SM"): dict(id="het-scheepvaartmuseum", naam="Het Scheepvaartmuseum",
                              plaats="Amsterdam", type="museum",
                              website="https://www.hetscheepvaartmuseum.nl",
                              opmerkingen="Voorheen Nederlands Scheepvaartmuseum."),
    ("Alkmaar", "RAA"): dict(id="regionaal-archief-alkmaar", naam="Regionaal Archief Alkmaar",
                             plaats="Alkmaar", type="archief",
                             website="https://www.regionaalarchiefalkmaar.nl"),
    ("Hoorn", "WA"): dict(id="westfries-archief", naam="Westfries Archief", plaats="Hoorn",
                          type="archief", website="https://www.westfriesarchief.nl"),
    ("Brussel", "KBR"): dict(id="kbr", naam="KBR (Koninklijke Bibliotheek van België)",
                             plaats="Brussel", land="België", type="bibliotheek",
                             website="https://www.kbr.be"),
    ("Groningen", "UBG"): dict(id="ub-groningen", naam="Universiteitsbibliotheek Groningen",
                               plaats="Groningen", type="bibliotheek",
                               website="https://www.rug.nl/library"),
    ("Utrecht", "UBU"): dict(id="ub-utrecht", naam="Universiteitsbibliotheek Utrecht",
                             plaats="Utrecht", type="bibliotheek",
                             website="https://www.uu.nl/universiteitsbibliotheek"),
    ("Leiden", "ELO"): dict(id="erfgoed-leiden", naam="Erfgoed Leiden en Omstreken", plaats="Leiden",
                            type="archief", website="https://www.erfgoedleiden.nl"),
    ("Arnhem", "HGA"): dict(id="gelders-archief", naam="Gelders Archief", plaats="Arnhem",
                            type="archief", website="https://www.geldersarchief.nl"),
    ("Haarlem", "NHA"): dict(id="noord-hollands-archief", naam="Noord-Hollands Archief",
                             plaats="Haarlem", type="archief",
                             website="https://noord-hollandsarchief.nl"),
    ("Alkmaar", "NHA"): dict(id="noord-hollands-archief"),
    ("Zwolle", "HCO"): dict(id="collectie-overijssel", naam="Collectie Overijssel", plaats="Zwolle",
                            type="archief", website="https://collectieoverijssel.nl",
                            opmerkingen="Voorheen Historisch Centrum Overijssel (HCO)."),
    ("Den Haag", "CBG"): dict(id="cbg", naam="CBG | Centrum voor familiegeschiedenis",
                              plaats="Den Haag", type="overig", website="https://cbg.nl"),
    ("Leeuwarden", "HCL"): dict(id="historisch-centrum-leeuwarden", naam="Historisch Centrum Leeuwarden",
                                plaats="Leeuwarden", type="archief",
                                website="https://historischcentrumleeuwarden.nl"),
    ("Amsterdam", "SA"): dict(id="stadsarchief-amsterdam", naam="Stadsarchief Amsterdam",
                              plaats="Amsterdam", type="archief",
                              website="https://www.amsterdam.nl/stadsarchief"),
    ("Groningen", "GA"): dict(id="groninger-archieven", naam="Groninger Archieven", plaats="Groningen",
                              type="archief", website="https://www.groningerarchieven.nl"),
    ("Maastricht", "RHCL"): dict(id="rhcl", naam="Regionaal Historisch Centrum Limburg",
                                 plaats="Maastricht", type="archief", website="https://www.rhcl.nl"),
    ("Delft", "Stadsarchief Delft"): dict(id="stadsarchief-delft", naam="Stadsarchief Delft",
                                          plaats="Delft", type="archief",
                                          website="https://stadsarchiefdelft.nl"),
    ("Rotterdam", "Stadsarchief Rotterdam"): dict(id="stadsarchief-rotterdam",
                                                  naam="Stadsarchief Rotterdam", plaats="Rotterdam",
                                                  type="archief",
                                                  website="https://stadsarchief.rotterdam.nl"),
}
# Lange namen die als tweede deel van de vindplaats voorkomen.
INSTELLING_PREFIX = {
    "Nederlands Scheepvaartmuseum": ("Amsterdam", "SM"),
}


# ---------------- Mellel-tekst uitlezen ----------------

def alinea_runs(p):
    uit = []
    for c in p:
        if c.tag != "c":
            continue
        delen = []

        def loop(el):
            for k in el:
                if k.tag == "note":
                    if k.tail:
                        delen.append(k.tail)
                    continue
                if k.text:
                    delen.append(k.text)
                loop(k)
                if k.tail:
                    delen.append(k.tail)

        if c.text:
            delen.append(c.text)
        loop(c)
        uit.append({"tekst": "".join(delen), "stijl": c.get("style", ""),
                    "cursief": "c" in c.get("var", "")})
    return uit


def laad_items(pad):
    root = ET.parse(pad).getroot()
    dt = root.find("root/text-model/document-text")
    sectie = list(dt)[5]  # de sectie 'Reisbescheiden' met appendix A en B
    items = []
    for i, p in enumerate(sectie.iter("p")):
        rs = alinea_runs(p)
        tekst = "".join(r["tekst"] for r in rs).strip()
        stijlen = sorted({r["stijl"] for r in rs if r["tekst"].strip()})
        items.append({"i": i, "pstijl": p.attrib.get("style", ""),
                      "tekst": tekst, "stijlen": stijlen, "runs": rs})
    return items


# ---------------- appendix A: reizigers ----------------

def eerste_runstijl(it):
    for r in it["runs"]:
        if r["tekst"].strip():
            return r["stijl"]
    return None


def is_letterkop(it):
    return (it["pstijl"] == "ps-1"
            or (it["stijlen"] == ["cs-2"] and len(it["tekst"]) <= 2))


def is_naamregel(it, vorige_leeg):
    """Lemma-regel: na een witregel, begint in de stijl 'Lemma' (cs-18)."""
    return (vorige_leeg and it["tekst"] and len(it["tekst"]) < 70
            and eerste_runstijl(it) == "cs-18"
            and not LABEL_RE.match(it["tekst"])
            and not JAARKOP_RE.match(it["tekst"]))


def parse_a(items, vanaf, tot):
    reizigers = []
    huidige = None
    laatste_label = None
    vorige_leeg = True
    for it in items[vanaf:tot]:
        if is_letterkop(it):
            vorige_leeg = True
            continue
        naamregel = is_naamregel(it, vorige_leeg)
        vorige_leeg = not it["tekst"]
        if naamregel:
            huidige = {"naam": it["tekst"].strip(), "typering": "", "biografie": [],
                       "labels": {}}
            reizigers.append(huidige)
            laatste_label = None
            continue
        if huidige is None or not it["tekst"]:
            if not it["tekst"]:
                laatste_label = None
            continue
        m = LABEL_RE.match(it["tekst"])
        if m:
            label = m.group(1).lower()
            huidige["labels"].setdefault(label, []).append(m.group(2).strip())
            laatste_label = label
        elif laatste_label:
            huidige["labels"][laatste_label].append(it["tekst"])
        elif not huidige["typering"]:
            huidige["typering"] = it["tekst"]
        else:
            huidige["biografie"].append(it["tekst"])
    return reizigers


# ---------------- appendix B: reisverslagen ----------------

def parse_ms_regel(it):
    tekst = "".join(r["tekst"] for r in it["runs"])
    velden = {"regel": tekst.strip()}

    m = re.search(r"(?:^|\s)Ms\.\s+", tekst)
    if m:
        voor, na = tekst[:m.start()].strip(), tekst[m.end():].strip()
        titelgrens = m.start()
        grens = re.search(r"\.\s+(?=M\.\s*\d{3}|LSD\b|[A-ZÈÉ][^,]*?\([A-Z]{2}\),|"
                          r"(?:Nederlands|Frans|Latijn|Duits|Engels|Italiaans|Spaans)\b|\d{4})", na)
        velden["vindplaats"] = (na[:grens.start()] if grens else na).rstrip(".").strip()
    else:
        mm0 = re.search(r"M\.\s*\d{3}", tekst)
        voor = tekst[:mm0.start()].strip() if mm0 else tekst
        titelgrens = mm0.start() if mm0 else len(tekst)

    # cursieve tekst vóór de vindplaats/kenmerken is de titel
    delen, pos = [], 0
    for r in it["runs"]:
        if r["cursief"] and pos < titelgrens:
            delen.append(r["tekst"][:max(0, titelgrens - pos)])
        pos += len(r["tekst"])
    cursief = "".join(delen).strip()
    velden["titel"] = (cursief or voor.rstrip(".")).strip().rstrip(".")

    mm = re.search(r"M\.\s*(\d{3})", tekst)
    if mm:
        velden["corpus"] = "M. " + mm.group(1)
    ml = re.search(r"LSD\s+([0-9]+[a-z]?|n\.v\.t\.?)", tekst)
    if ml:
        velden["lsd"] = ml.group(1)
    md = re.search(r"\((\d+)\s*dagen\)", tekst)
    if md:
        velden["dagen"] = int(md.group(1))
    mr = re.search(r"Route:\s*(.+?)\.\s*(Educatie|Cultuur/vermaak|Cultuur|Vermaak|"
                   r"Zaken|Diplomatie|Militair|Anders|Religie)\.?\s*$", tekst)
    if mr:
        velden["route"] = [s.strip() for s in mr.group(1).split(",")]
        velden["doel"] = mr.group(2)
    else:
        mr2 = re.search(r"Route:\s*(.+?)\.?\s*$", tekst)
        if mr2:
            velden["route"] = [s.strip() for s in mr2.group(1).split(",")]
    mv = re.search(r"([A-ZÈÉ][^.,;–()]*?)\s*(?:\(([A-Z]{2})\))?,\s*"
                   r"((?:ca\.\s*)?\d{1,2}\s+\w+\s+\d{4}|\d{4})\s*–\s*"
                   r"([^.,;–()]*?)\s*(?:\(([A-Z]{2})\))?,\s*"
                   r"((?:ca\.\s*)?\d{1,2}\s+\w+\s+\d{4}|\d{4})", tekst)
    if mv:
        velden["vertrek_plaats"], velden["vertrek_land"], velden["vertrek_datum"] = \
            mv.group(1), mv.group(2), mv.group(3)
        velden["aankomst_plaats"], velden["aankomst_land"], velden["aankomst_datum"] = \
            mv.group(4), mv.group(5), mv.group(6)
    mt = re.search(r"(?:^|\.\s)\s*((?:Nederlands|Frans|Latijn|Duits|Engels|Italiaans|"
                   r"Spaans)(?:\s*(?:,|/| en )\s*(?:Nederlands|Frans|Latijn|Duits|"
                   r"Engels|Italiaans|Spaans))*)\s*[,.]", tekst)
    if mt:
        velden["taal"] = mt.group(1)
    mo = re.search(r"((?:ff|pp)\.\s*\[?\d+\]?[^.]*)", tekst)
    if mo:
        velden["omvang"] = mo.group(1).strip()
    return velden


def parse_b(items, vanaf):
    entries = []
    entry = None
    doel = None
    jaar_wachtend = None
    laatste_label = None
    for it in items[vanaf:]:
        if not it["tekst"]:
            laatste_label = None
            continue
        mkop = re.match(r"^(\d+)\.\s+(.*)$", it["tekst"])
        if mkop and "cs-18" in it["stijlen"] and len(mkop.group(2)) < 80:
            entry = {"nr": int(mkop.group(1)), "kop": mkop.group(2).strip(),
                     "beschrijving": [], "labels": {}, "verslagen": []}
            entries.append(entry)
            doel = entry
            jaar_wachtend = None
            laatste_label = None
            continue
        if entry is None:
            continue
        if JAARKOP_RE.match(it["tekst"]):
            jaar_wachtend = it["tekst"]
            laatste_label = None
            continue
        mlab = LABEL_RE.match(it["tekst"])
        if not mlab and (re.search(r"(?:^|\s)Ms\.\s+\S", it["tekst"])
                         or re.search(r"M\.\s*\d{3}", it["tekst"])):
            verslag = {"jaar": jaar_wachtend, "ms": parse_ms_regel(it),
                       "beschrijving": [], "labels": {}}
            entry["verslagen"].append(verslag)
            doel = verslag
            jaar_wachtend = None
            laatste_label = None
            continue
        if mlab:
            label = mlab.group(1).lower()
            doel["labels"].setdefault(label, []).append(mlab.group(2).strip())
            laatste_label = label
        elif laatste_label:
            doel["labels"][laatste_label].append(it["tekst"])
        else:
            doel["beschrijving"].append(it["tekst"])
    return entries


# ---------------- omzetting naar YAML-records ----------------

def slug(tekst):
    tekst = unicodedata.normalize("NFKD", tekst).encode("ascii", "ignore").decode()
    tekst = re.sub(r"[^a-z0-9]+", "-", tekst.lower()).strip("-")
    return tekst or "onbekend"


def leefdata(typering):
    pat = re.compile(rf"(?:^|\.\s+)(?:(?P<gp>[A-Z][^.,–()]*?),\s*)?(?P<gd>{DATUM_DEEL})"
                     rf"\s*–\s*(?:(?P<op>[A-Z][^.–]*?),\s*)?(?P<od>{DATUM_DEEL})\.")
    m = pat.search(typering)
    if not m:
        return None, None
    grens = typering.find("Maakte")
    if grens != -1 and m.start() > grens:
        return None, None

    def deel(plaats, datum):
        d = {}
        jaar = re.findall(r"\d{4}", datum)
        if jaar:
            d["jaar"] = int(jaar[-1])
        if datum and not re.fullmatch(r"\d{4}", datum.strip()):
            d["datum"] = datum.strip()
        if plaats:
            d["plaats"] = plaats.strip()
        return d or None

    return deel(m.group("gp"), m.group("gd")), deel(m.group("op"), m.group("od"))


def religie_uit(typering):
    m = re.search(r"\b(" + "|".join(RELIGIES) + r")\b", typering)
    return m.group(1) if m else None


def splits_vindplaats(vindplaats):
    """'Den Haag, KB, KB 70 H 28-I' -> (instelling-record, signatuur, extra)."""
    delen = [d.strip() for d in vindplaats.split(";")]
    eerste, extra = delen[0], delen[1:]
    parts = [p.strip() for p in eerste.split(",")]
    if len(parts) < 2:
        return None, eerste, extra
    plaats, tweede = parts[0], parts[1]
    for prefix, sleutel in INSTELLING_PREFIX.items():
        if tweede.startswith(prefix):
            rest = tweede[len(prefix):].strip()
            signatuur = ", ".join([rest] + parts[2:]) if rest or parts[2:] else ""
            return sleutel, signatuur.strip(", "), extra
    sleutel = (plaats, tweede)
    signatuur = ", ".join(parts[2:])
    return sleutel, signatuur, extra


def schrijf(map_, record):
    pad = DATA / map_ / f"{record['id']}.yaml"
    pad.parent.mkdir(parents=True, exist_ok=True)
    schoon = {k: v for k, v in record.items() if v not in (None, "", [], {})}
    pad.write_text(yaml.safe_dump(schoon, allow_unicode=True, sort_keys=False,
                                  width=88), encoding="utf-8")


def hoofd():
    if len(sys.argv) < 2:
        sys.exit("gebruik: python3 scripts/import_gemaakt_op_reis.py <main.xml>")
    items = laad_items(sys.argv[1])
    koppen = {it["tekst"]: it["i"] for it in items if it["pstijl"] == "ps-1" and it["tekst"]}
    ruwe_reizigers = parse_a(items, koppen["Reizigers"] + 1, koppen["Reisverslagen"] - 1)
    entries = parse_b(items, koppen["Reisverslagen"] + 1)

    gebruikt_instelling = {}   # sleutel -> record
    onbekende_instellingen = set()

    # --- reizigers ---
    lemma_naar_id = {}
    for r in ruwe_reizigers:
        naam = r["naam"]
        varianten = None
        mv = re.match(r"^(.*?)\s*\[(?:ook:)?\s*(.*)\]$", naam)
        if mv:
            naam, varianten = mv.group(1).strip(), [v.strip() for v in mv.group(2).split(";")]
        rid = slug(naam)
        lemma_naar_id[naam] = rid
        geboren, overleden = leefdata(r["typering"])
        record = {
            "id": rid,
            "naam": naam,
            "naamsvarianten": varianten,
            "geboren": geboren,
            "overleden": overleden,
            "religie": religie_uit(r["typering"]),
            "korte_typering": r["typering"],
            "biografie": "\n\n".join(r["biografie"]),
            "reizen_vermeld": r["labels"].get("reizen"),
            "verslagen_vermeld": r["labels"].get("verslagen", []) + r["labels"].get("verslag", []),
            "addenda": r["labels"].get("addenda"),
            "correspondentie": r["labels"].get("correspondentie"),
            "poezie": r["labels"].get("poëzie"),
            "literatuur": r["labels"].get("literatuur"),
            "externe_ids": {},
            "bronnen": ["gemaakt-op-reis"],
        }
        schrijf("reizigers", record)

    def normaliseer(naam):
        """Naamvorm voor vergelijking: zonder varianten, haakjes, sr./jr., trema's."""
        n = re.sub(r"\s*\[.*?\]", "", naam)          # [ook: ...]
        n = re.sub(r"\(-[^)]*\)", "", n)             # aangetrouwde naam (-Bock)
        n = re.sub(r"\s*\(\d+\)", "", n)             # volgnummers (1) (2)
        n = re.sub(r"\(([a-z]{1,2})\)", r"\1", n)    # de(r) -> der
        n = re.sub(r"\s*\([^)]*\)", "", n)           # overige haakjes (varianten)
        n = re.sub(r"\b(sr|jr)\.?\s*", "", n)
        n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
        return re.sub(r"\s+", " ", n).lower().strip(" .,")

    genormaliseerd = {}
    for lemma, lid in lemma_naar_id.items():
        genormaliseerd.setdefault(normaliseer(lemma), []).append(lid)

    def zoek_auteurs(kop):
        m = re.match(r"^(.*?)(?:\s+(\d{4}(?:-\d{2,4})?))?$", kop)
        naamdeel, periode = m.group(1).strip().strip("[]").rstrip(","), m.group(2)
        if naamdeel.lower().startswith("anoniem"):
            return [], periode, []
        kandidaten = []
        if ", " in naamdeel and " en " in naamdeel.split(", ", 1)[1]:
            achternaam, vn = naamdeel.split(", ", 1)
            stukken = [s.strip() for s in vn.split(" en ")]
            staart = stukken[-1].split()
            deeltjes = [w for w in staart if w.islower()]
            for s in stukken:
                woorden = s.split()
                if not any(w.islower() for w in woorden):
                    woorden += deeltjes
                kandidaten.append(f"{achternaam}, {' '.join(woorden)}")
        else:
            kandidaten.append(naamdeel)
        gevonden, vermist = [], []
        for k in kandidaten:
            if k in lemma_naar_id:
                gevonden.append(lemma_naar_id[k])
                continue
            treffers = genormaliseerd.get(normaliseer(k), [])
            if len(treffers) == 1:
                gevonden.append(treffers[0])
            elif len(treffers) > 1:
                vermist.append(f"{k} (meerdere kandidaten in appendix A)")
            else:
                # geen lemma in appendix A: maak een minimale reiziger aan
                rid = slug(k)
                if k not in lemma_naar_id:
                    lemma_naar_id[k] = rid
                    genormaliseerd.setdefault(normaliseer(k), []).append(rid)
                    schrijf("reizigers", {
                        "id": rid, "naam": k,
                        "opmerkingen": "Aangemaakt op basis van appendix B van Gemaakt "
                                       "op reis; geen lemma in appendix A.",
                        "bronnen": ["gemaakt-op-reis"], "controle_nodig": True})
                gevonden.append(rid)
        return gevonden, periode, vermist

    # --- manuscripten en reizen ---
    gebruikte_ids = set()
    n_ms = n_reis = 0
    for e in entries:
        auteurs, periode, vermist = zoek_auteurs(e["kop"])
        # band-regels (alleen vindplaats + LSD) van echte verslagen scheiden
        band = None
        verslagen = []
        for v in e["verslagen"]:
            ms = v["ms"]
            if (not ms.get("titel") and "corpus" not in ms
                    and "vertrek_datum" not in ms and "route" not in ms):
                band = v
            else:
                verslagen.append(v)
        if band and not verslagen:
            verslagen, band = [band], None

        basis = slug(e["kop"].split(",")[0]) if not e["kop"].lower().startswith("anoniem") \
            else slug("anoniem-" + (periode or ""))

        for v in verslagen:
            ms = v["ms"]
            jaar = v["jaar"] or (ms.get("vertrek_datum") or "")[-4:] or periode or "sd"
            mid = f"{basis}-{slug(str(jaar))}"
            volg = 2
            while mid in gebruikte_ids:
                mid = f"{basis}-{slug(str(jaar))}-{volg}"
                volg += 1
            gebruikte_ids.add(mid)

            vindplaats = ms.get("vindplaats") or (band and band["ms"].get("vindplaats"))
            sleutel = signatuur = None
            extra = []
            if vindplaats:
                sleutel, signatuur, extra = splits_vindplaats(vindplaats)
            instelling_id = None
            if sleutel:
                if sleutel in INSTELLINGEN:
                    rec = INSTELLINGEN[sleutel]
                    instelling_id = rec["id"]
                    volledig = next((r for k, r in INSTELLINGEN.items()
                                     if r["id"] == rec["id"] and r.get("naam")), rec)
                    gebruikt_instelling[rec["id"]] = volledig
                else:
                    plaats, afk = sleutel
                    instelling_id = slug(f"{afk}-{plaats}")
                    gebruikt_instelling.setdefault(instelling_id, dict(
                        id=instelling_id, naam=f"{afk} ({plaats})", plaats=plaats,
                        controle_nodig=True,
                        opmerkingen="Automatisch aangemaakt bij import; naam en gegevens controleren."))
                    onbekende_instellingen.add(f"{afk} ({plaats})")

            opmerkingen = []
            if band:
                bandtekst = " ".join(band["beschrijving"]) if band.get("beschrijving") else ""
                opmerkingen.append(
                    f"Onderdeel van een convoluut: {band['ms'].get('vindplaats', '')}."
                    + (f" {bandtekst}" if bandtekst else ""))
            if e["beschrijving"] and len(verslagen) > 1:
                opmerkingen.append("Band/convoluut: " + " ".join(e["beschrijving"]))
            if extra:
                opmerkingen.append("Ook overgeleverd: " + "; ".join(extra) + ".")
            if vermist:
                opmerkingen.append("Auteur(s) niet automatisch gekoppeld: " + "; ".join(vermist) + ".")

            beschrijving = list(v["beschrijving"])
            if len(verslagen) == 1 and e["beschrijving"]:
                beschrijving = e["beschrijving"] + beschrijving

            labels = dict(e["labels"]) if len(verslagen) == 1 else {}
            for k, w in v["labels"].items():
                labels.setdefault(k, []).extend(x for x in w if x not in labels.get(k, []))
            edities = labels.get("editie", []) + labels.get("edities", [])
            edities += ["Transcriptie: " + t for t in
                        labels.get("transcriptie", []) + labels.get("transcripties", [])]

            lsd = ms.get("lsd") or (band and band["ms"].get("lsd"))
            if lsd and lsd.startswith("n.v.t"):
                lsd = None

            reistype = DOEL_NAAR_REISTYPE.get(ms.get("doel", ""), "onbekend")
            rid = f"{mid}-reis"
            record_ms = {
                "id": mid,
                "titel_aanduiding": ms["titel"] or f"Reisverslag {e['kop']}",
                "reizen": [rid],
                "auteurs": auteurs,
                "instelling": instelling_id,
                "signatuur": signatuur,
                "taal": ms.get("taal"),
                "datering": re.sub(r"\s+[IVX]+$", "", v["jaar"]) if v["jaar"] else periode,
                "omvang": ms.get("omvang"),
                "corpus_gor": ms.get("corpus"),
                "repertorium_lsd": lsd,
                "beschrijving": "\n\n".join(beschrijving),
                "digitalisering": {"status": "onbekend"},
                "transcriptie": {"status": "onbekend"},
                "edities": edities or None,
                "addenda": labels.get("addenda"),
                "correspondentie": labels.get("correspondentie"),
                "poezie": labels.get("poëzie"),
                "literatuur": labels.get("literatuur"),
                "opmerkingen": " ".join(opmerkingen),
                "bronnen": ["gemaakt-op-reis"],
                "controle_nodig": True if (vermist or not instelling_id) else None,
            }
            schrijf("manuscripten", record_ms)
            n_ms += 1

            route_punten = []
            for kant in ("vertrek", "aankomst"):
                if ms.get(f"{kant}_plaats"):
                    punt = {"plaats": ms[f"{kant}_plaats"]}
                    land = LANDEN.get(ms.get(f"{kant}_land") or "")
                    if land:
                        punt["land_modern"] = land
                    punt["datum"] = ms.get(f"{kant}_datum")
                    route_punten.append(punt)
            def draai(naam):
                if ", " in naam:
                    a, v = naam.split(", ", 1)
                    return f"{v} {a}"
                return naam

            auteursnamen = [draai(naam) for naam, i in lemma_naar_id.items() if i in auteurs]
            titel_wie = " en ".join(auteursnamen) if auteursnamen else \
                draai(e["kop"]) if not e["kop"].lower().startswith("anoniem") else "een onbekende reiziger"
            jaartekst = v["jaar"] or periode or (ms.get("vertrek_datum") or "")[-4:]
            record_reis = {
                "id": rid,
                "titel": f"{REISTYPE_TITEL[reistype]} van {titel_wie}"
                         + (f" ({jaartekst})" if jaartekst else ""),
                "reizigers": auteurs,
                "reistype": reistype,
                "vertrek": ms.get("vertrek_datum"),
                "terugkeer": ms.get("aankomst_datum"),
                "reisdagen": ms.get("dagen"),
                "gebieden": ms.get("route"),
                "route": route_punten or None,
                "bronnen": ["gemaakt-op-reis"],
            }
            schrijf("reizen", record_reis)
            n_reis += 1

    for rec in gebruikt_instelling.values():
        if rec.get("naam"):
            schrijf("instellingen", rec)

    print(f"Geschreven: {len(ruwe_reizigers)} reizigers, {n_ms} manuscripten, "
          f"{n_reis} reizen, {len(gebruikt_instelling)} instellingen.")
    if onbekende_instellingen:
        print("Onbekende instellingen (controle nodig):", "; ".join(sorted(onbekende_instellingen)))


if __name__ == "__main__":
    hoofd()
