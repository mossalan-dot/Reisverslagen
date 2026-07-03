# Datamodel

Vier entiteiten, elk als YAML-bestand in de bijbehorende map onder `data/`. De bestandsnaam is de `id` (bijv. `data/reizigers/coenraad-ruysch.yaml`). De verrijkingen (portretten, opleiding, reisgezellen, brieven, poëzie, addenda) staan **genest** in het reiziger- of reisbestand waar ze bij horen; ze zijn geen aparte bestanden.

Algemene regels:

- **`id`** is verplicht, uniek binnen de hele dataset, en bestaat uit kleine letters, cijfers en koppeltekens. Verwijzingen tussen entiteiten lopen via deze id's.
- Onbekende gegevens: laat het veld weg of leeg.
- **`controle_nodig: true`** markeert een record dat nog geverifieerd moet worden.
- **`bronnen`** (lijst) vermeldt de herkomst, bijv. `gemaakt-op-reis-database`.
- De gegevens worden gegenereerd met `scripts/import_filemaker.py`; handmatige wijzigingen in `data/` blijven bewaard zolang er niet opnieuw wordt geïmporteerd.

## Reiziger (`data/reizigers/`)

| Veld | Verplicht | Toelichting |
|---|---|---|
| `id` | ja | |
| `naam` | ja | Lemma-vorm `Achternaam, Voornaam tussenvoegsel` (sorteersleutel) |
| `volledige_naam` | nee | Weergavenaam in leesvolgorde |
| `naamsvarianten` | nee | Lijst van naam-, spellings- en doopnaamvarianten |
| `titel`, `achtervoegsel` | nee | Adellijke/andere titel |
| `geslacht` | nee | `Man` / `Vrouw` |
| `geboren` / `overleden` | nee | `{jaar, datum, plaats, provincie}` |
| `religie` | nee | |
| `is_auteur` | nee | `true` als de reiziger zelf een verslag schreef |
| `korte_typering` | nee | Eén regel: eerste reis, leeftijd |
| `biografie` | nee | Biografische schets |
| `genealogie` | nee | `{vader, moeder, echtgenoten[], kinderen[], broers_zussen[], andere_familie[]}` |
| `opleiding` | nee | Lijst van `{universiteit, richting, datum, incipit, opmerking, bron}` |
| `portretten` | nee | Lijst van `{titel, geportretteerde, vervaardiger, jaar, bron, link, beschrijving}` |
| `literatuur` | nee | Lijst |
| `bronnen`, `controle_nodig` | nee | |

## Reis (`data/reizen/`)

| Veld | Verplicht | Toelichting |
|---|---|---|
| `id` | ja | |
| `titel` | ja | Eigentijdse titel of moderne aanduiding |
| `reizigers` | nee | Lijst van reiziger-id's (leeg bij anonieme reizen) |
| `reistype` | nee | `educatiereis`, `diplomatieke reis`, `plezierreis`, `handelsreis`, `militaire reis`, `pelgrimsreis`, `overig`, `onbekend` |
| `jaren` | nee | Bijv. `1674-1677` |
| `vertrek` / `terugkeer` | nee | Datum of jaar |
| `reisdagen` | nee | |
| `gebieden` | nee | Lijst van bezochte landen/regio's |
| `route` | nee | Lijst van `{plaats, land_modern, datum, geo: {lat, lon}}` |
| `manuscript` | nee | Manuscript-id (indien een handschrift bewaard is) |
| `beschrijving` | nee | Inhoudsbeschrijving van reis en verslag |
| `reisgezellen` | nee | Lijst van `{naam, jaren, opmerkingen}` |
| `brieven` | nee | Lijst van `{verzender, ontvanger, datum, plaats/land verzender/ontvanger, relatie, taal, bron, link, opmerking, tekst}` |
| `poezie` | nee | Lijst van `{titel, dichter, aan, datum, locatie, taal, bron, link, beschrijving, tekst}` |
| `addenda` | nee | Lijst van `{type, auteur, beschrijving, datum, relatie, taal, bron, link, locatie, transcriptie, foto}` |
| `literatuur` | nee | |
| `bronnen`, `controle_nodig` | nee | |

## Manuscript (`data/manuscripten/`)

| Veld | Verplicht | Toelichting |
|---|---|---|
| `id` | ja | |
| `titel_aanduiding` | ja | Eigentijdse titel of moderne aanduiding |
| `reizen` | nee | Lijst van reis-id's die het manuscript beschrijft |
| `auteurs` | nee | Lijst van reiziger-id's |
| `instelling` | nee | Instelling-id van de huidige bewaarplaats |
| `signatuur` | nee | Actuele signatuur of inventarisnummer |
| `permalink` | nee | Stabiele url naar de beschrijving bij de instelling |
| `taal` | nee | |
| `omvang` | nee | Bijv. `ff. 100` |
| `incompleet` | nee | `true` bij een onvolledig handschrift |
| `beschrijving` | nee | |
| `corpus_gor` | nee | Corpusnummer in *Gemaakt op reis* (bijv. `M. 001`) |
| `repertorium_lsd` | nee | Nummer in Lindeman/Scherf/Dekker |
| `edities` | nee | Lijst van edities |
| `digitalisering` | nee | `{status, url, iiif_manifest}` — status: `geen`, `gedeeltelijk`, `volledig`, `onbekend` |
| `transcriptie` | nee | `{status, url, door}` |
| `laatst_gecontroleerd` | nee | Datum waarop vindplaats/signatuur is geverifieerd |
| `opmerkingen`, `bronnen`, `controle_nodig` | nee | |

## Instelling (`data/instellingen/`)

| Veld | Verplicht | Toelichting |
|---|---|---|
| `id` | ja | |
| `naam` | ja | Actuele naam |
| `plaats`, `land` | nee | |
| `type` | nee | `archief`, `bibliotheek`, `museum`, `particulier`, `overig` |
| `website` | nee | |
| `opmerkingen` | nee | O.a. naamgeschiedenis en fusies |
