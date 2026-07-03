# Reisverslagen

**Compendium van handgeschreven reisverslagen van reizigers uit de Nederlanden (zeventiende eeuw)**

Dit project bouwt aan een volledig en actueel overzicht van handgeschreven reisverslagen van reizigers uit de Noordelijke en Zuidelijke Nederlanden, waar ter wereld die manuscripten ook bewaard worden. Het vertrekpunt is de zeventiende eeuw; latere uitbreiding naar vroegere en latere periodes en naar gedrukte reisteksten is voorzien.

## Achtergrond

Het compendium bouwt voort op twee onvolledige voorgangers:

- Het repertorium van R. Lindeman, Y. Scherf en R.M. Dekker, *Reisverslagen van Noord-Nederlanders van de zestiende tot begin negentiende eeuw. Een chronologische lijst* (Rotterdam 1994), online raadpleegbaar via [egodocument.net](http://www.egodocument.net/reisverslagen.html);
- De appendices (reizigers, reizen, manuscripten) in Alan Moss, *Gemaakt op reis. Identiteitsvorming in verslagen van de Nederlandse educatiereis (1648–1713)* (proefschrift Radboud Universiteit 2022; handelseditie Hilversum: Verloren 2023), [online beschikbaar](https://repository.ubn.ru.nl/handle/2066/247895).

Het compendium wil per manuscript de **actuele vindplaats** geven (instelling, collectie, signatuur, permalink) en de **status** bijhouden: is het verslag gedigitaliseerd, getranscribeerd en/of uitgegeven? Daarnaast is er ruimte voor verrijking met transcripties, afbeeldingen en geodata.

## Opzet

De gegevens staan als leesbare YAML-bestanden in de map `data/`, verdeeld over vier entiteiten:

| Map | Entiteit | Voorbeeld |
|---|---|---|
| `data/reizigers/` | Eén bestand per reiziger | biografische gegevens, externe identifiers |
| `data/reizen/` | Eén bestand per reis | reistype, periode, route (met geodata) |
| `data/manuscripten/` | Eén bestand per manuscript | vindplaats, signatuur, status |
| `data/instellingen/` | Eén bestand per bewaarinstelling | naam, plaats, website, naamgeschiedenis |

Eén reiziger kan meerdere reizen hebben gemaakt; één reis kan in meerdere handschriften zijn overgeleverd (klad, net, kopie); één handschrift kan meerdere reizen bevatten. Het model ondersteunt al die relaties. Zie [DATAMODEL.md](DATAMODEL.md) voor de volledige veldbeschrijving.

## Website bouwen

Het script `scripts/bouw.py` controleert alle gegevens (verplichte velden, geldige verwijzingen) en genereert een doorzoekbare, zelfstandige website in `docs/`:

```
python3 scripts/bouw.py
```

De uitvoer bestaat uit `docs/index.html` (de complete website in één bestand, zonder externe afhankelijkheden) en `docs/data.json` (de volledige dataset als open data). De map `docs/` kan rechtstreeks op elke webserver worden gezet of via GitHub Pages worden gepubliceerd — zie [PUBLICEREN.md](PUBLICEREN.md) voor de mogelijkheden, inclusief automatische publicatie naar een eigen server.

## Bijdragen

Aanvullingen, correcties, transcripties en scans zijn welkom. Zie [BIJDRAGEN.md](BIJDRAGEN.md).

## Stappenplan

- [x] Datamodel en repository-opzet
- [x] Doorzoekbare website (prototype)
- [ ] Basisvulling: appendices *Gemaakt op reis* invoeren
- [ ] Basisvulling: repertorium Lindeman/Scherf/Dekker (zeventiende eeuw) invoeren en actualiseren
- [ ] Signaturen en permalinks controleren bij de instellingen
- [ ] Kaartweergave op basis van geodata
- [ ] Suggestieformulier op de website
- [ ] Uitbreiding naar zestiende en achttiende eeuw
- [ ] Uitbreiding met gedrukte reisteksten
