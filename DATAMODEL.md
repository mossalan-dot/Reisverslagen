# Datamodel

Vier entiteiten, elk als YAML-bestand in de bijbehorende map onder `data/`. De bestandsnaam is vrij, maar gebruik bij voorkeur de `id` als naam (bijv. `data/reizigers/hooft-arnout-hellemans.yaml`).

Algemene regels:

- **`id`** is verplicht, uniek binnen de hele dataset, en bestaat uit kleine letters, cijfers en koppeltekens (bijv. `hooft-arnout-hellemans`). Verwijzingen tussen entiteiten lopen altijd via deze id's.
- Onbekende gegevens: laat het veld weg of leeg. Gebruik geen "?" in datavelden; twijfel hoort in `opmerkingen`.
- **`controle_nodig: true`** markeert een record waarvan de gegevens nog geverifieerd moeten worden (bijv. verouderde signatuur uit het repertorium).
- **`bronnen`** (lijst) vermeldt waar de gegevens vandaan komen, bijv. `repertorium-lsd`, `gemaakt-op-reis`, `eigen-onderzoek`, of een vrije literatuurverwijzing.
- Jaartallen als getal (`1649`); preciezere dateringen als tekst (`"1649-05-17"`, `"circa 1650"`).

## Reiziger (`data/reizigers/`)

| Veld | Verplicht | Toelichting |
|---|---|---|
| `id` | ja | |
| `naam` | ja | Weergavenaam, bijv. `Arnout Hellemans Hooft` |
| `geboren` | nee | `{jaar, datum, plaats}` |
| `overleden` | nee | `{jaar, datum, plaats}` |
| `herkomst` | nee | Stad/gewest van herkomst |
| `religie` | nee | |
| `beroep_functie` | nee | Beroep of latere maatschappelijke functie(s) |
| `familie` | nee | Relevante familierelaties |
| `externe_ids` | nee | `{wikidata, viaf, dbnl, ecartico, ...}` — alleen de code, geen url |
| `literatuur` | nee | Lijst van verwijzingen |
| `opmerkingen` | nee | |
| `bronnen` | nee | Lijst |
| `controle_nodig` | nee | `true`/`false` |

## Reis (`data/reizen/`)

| Veld | Verplicht | Toelichting |
|---|---|---|
| `id` | ja | |
| `titel` | ja | Bijv. `Educatiereis van Arnout Hellemans Hooft` |
| `reizigers` | ja | Lijst van reiziger-id's |
| `reistype` | nee | Eén uit: `educatiereis`, `pelgrimsreis`, `diplomatieke reis`, `handelsreis`, `militaire reis`, `plezierreis`, `gemengd`, `overig`, `onbekend` |
| `vertrek` | nee | Jaar of datum |
| `terugkeer` | nee | Jaar of datum |
| `gebieden` | nee | Lijst van bezochte landen/regio's (grofmazig, voor filtering) |
| `route` | nee | Lijst van plaatsen: `{plaats, land_modern, datum, geo: {lat, lon}, geonames, wikidata}` |
| `reisgenoten` | nee | Vrije tekst voor gezelschap dat geen eigen record heeft |
| `opmerkingen` | nee | |
| `bronnen` | nee | |
| `controle_nodig` | nee | |

## Manuscript (`data/manuscripten/`)

| Veld | Verplicht | Toelichting |
|---|---|---|
| `id` | ja | |
| `titel_aanduiding` | ja | Eigentijdse titel of moderne aanduiding |
| `reizen` | nee | Lijst van reis-id's die het manuscript beschrijft |
| `auteurs` | nee | Lijst van reiziger-id's (schrijver kan afwijken van reiziger, bijv. kopiist) |
| `instelling` | nee | Instelling-id van de huidige bewaarplaats (weglaten indien onbekend of particulier bezit; licht toe in `opmerkingen`) |
| `collectie` | nee | Archief-/collectienaam binnen de instelling |
| `signatuur` | nee | Actuele signatuur of inventarisnummer |
| `permalink` | nee | Stabiele url naar de beschrijving bij de instelling |
| `taal` | nee | Bijv. `Nederlands`, `Frans` |
| `datering` | nee | Ontstaanstijd van het handschrift |
| `manuscripttype` | nee | Eén uit: `klad`, `net`, `kopie`, `brieven`, `overig`, `onbekend` |
| `omvang` | nee | Bijv. `1 deel, 213 fol.` |
| `digitalisering` | nee | `{status, url, iiif_manifest}` — status: `geen`, `gedeeltelijk`, `volledig`, `onbekend` |
| `transcriptie` | nee | `{status, url, door}` — status als hierboven |
| `edities` | nee | Lijst van gedrukte of digitale edities |
| `repertorium_lsd` | nee | Nummer in Lindeman/Scherf/Dekker |
| `literatuur` | nee | |
| `laatst_gecontroleerd` | nee | Datum waarop vindplaats/signatuur voor het laatst is geverifieerd |
| `opmerkingen` | nee | |
| `bronnen` | nee | |
| `controle_nodig` | nee | |

## Instelling (`data/instellingen/`)

| Veld | Verplicht | Toelichting |
|---|---|---|
| `id` | ja | |
| `naam` | ja | Actuele naam |
| `plaats` | nee | |
| `land` | nee | |
| `type` | nee | Eén uit: `archief`, `bibliotheek`, `museum`, `particulier`, `overig` |
| `website` | nee | |
| `opmerkingen` | nee | O.a. naamgeschiedenis en fusies (bijv. voormalige rijksarchieven) |
