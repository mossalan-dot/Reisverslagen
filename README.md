# Reisverslagen

**Compendium van handgeschreven reisverslagen van reizigers uit de Nederlanden (zeventiende eeuw)**

Dit project bouwt aan een volledig en actueel overzicht van handgeschreven reisverslagen van reizigers uit de Noordelijke en Zuidelijke Nederlanden, waar ter wereld die manuscripten ook bewaard worden. Het vertrekpunt is de zeventiende eeuw; latere uitbreiding naar vroegere en latere periodes en naar gedrukte reisteksten is voorzien.

## Achtergrond

Het compendium bouwt voort op drie bronnen:

- De onderzoeksdatabase (FileMaker) van Alan Moss, met ruim 300 reizigers, 650 reizen en talrijke verrijkingen — de huidige ruggengraat van de gegevens;
- De appendices (reizigers, reizen, manuscripten) in Alan Moss, *Gemaakt op reis. Identiteitsvorming in verslagen van de Nederlandse educatiereis (1648–1713)* (proefschrift Radboud Universiteit 2022; handelseditie Hilversum: Verloren 2023), [online beschikbaar](https://repository.ubn.ru.nl/handle/2066/247895);
- Het repertorium van R. Lindeman, Y. Scherf en R.M. Dekker, *Reisverslagen van Noord-Nederlanders van de zestiende tot begin negentiende eeuw. Een chronologische lijst* (Rotterdam 1994), online raadpleegbaar via [egodocument.net](http://www.egodocument.net/reisverslagen.html) — waarnaar per manuscript met een LSD-nummer wordt verwezen.

Het compendium wil per manuscript de **actuele vindplaats** geven (instelling, signatuur) en de **status** bijhouden: is het verslag gedigitaliseerd, getranscribeerd en/of uitgegeven? Reizigers en reizen zijn bovendien verrijkt met genealogie, portretten, correspondentie, poëzie, reisgezellen en addenda.

De gegevens worden opgebouwd uit de database met `scripts/import_filemaker.py`; de database-export zelf hoort niet in de repository.

## Opzet

De gegevens staan als leesbare YAML-bestanden in de map `data/`, verdeeld over vier entiteiten:

| Map | Entiteit | Voorbeeld |
|---|---|---|
| `data/reizigers/` | Eén bestand per reiziger | biografie, genealogie, geneste portretten en opleiding |
| `data/reizen/` | Eén bestand per reis | reistype, periode, route, geneste reisgezellen, brieven, poëzie en addenda |
| `data/manuscripten/` | Eén bestand per manuscript | vindplaats, signatuur, corpus- en LSD-nummer, status |
| `data/instellingen/` | Eén bestand per bewaarinstelling | naam, plaats, website, naamgeschiedenis |

Eén reiziger kan meerdere reizen hebben gemaakt; een reis met een bewaard handschrift verwijst naar een manuscriptrecord. De verrijkingen (portretten, brieven, poëzie, addenda, reisgezellen) staan genest in het reiziger- of reisbestand waar ze bij horen. Zie [DATAMODEL.md](DATAMODEL.md) voor de volledige veldbeschrijving.

## Website bouwen

Het script `scripts/bouw.py` controleert alle gegevens (verplichte velden, geldige verwijzingen) en genereert een doorzoekbare, zelfstandige website in `docs/`:

```
python3 scripts/bouw.py
```

De uitvoer bestaat uit `docs/index.html` (de doorzoekbare website; de lange brief- en gedichtteksten worden daarin bij het openen van een detail nageladen uit `data.json`) en `docs/data.json` (de volledige dataset als open data). De map `docs/` kan rechtstreeks op elke webserver worden gezet of via GitHub Pages worden gepubliceerd — zie [PUBLICEREN.md](PUBLICEREN.md) voor de mogelijkheden, inclusief automatische publicatie naar een eigen server.

## Bijdragen

Aanvullingen, correcties, transcripties en scans zijn welkom. Zie [BIJDRAGEN.md](BIJDRAGEN.md).

## Stappenplan

- [x] Datamodel en repository-opzet
- [x] Doorzoekbare website
- [x] Basisvulling uit de onderzoeksdatabase (310 reizigers, 651 reizen, 196 manuscripten, plus verrijkingen)
- [x] Publicatie (GitHub Pages)
- [ ] Signaturen en permalinks controleren bij de instellingen; permalinks per manuscript toevoegen
- [ ] Digitaliserings- en transcriptiestatus per manuscript invullen
- [ ] Kaartweergave op basis van geodata (coördinaten per route-plaats)
- [ ] Repertorium Lindeman/Scherf/Dekker naast de LSD-nummers leggen ter aanvulling
- [ ] Suggestieformulier op de website
- [ ] Uitbreiding naar zestiende en achttiende eeuw
- [ ] Uitbreiding met gedrukte reisteksten
