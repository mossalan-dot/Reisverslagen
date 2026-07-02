# Bijdragen

Het compendium groeit door aanvullingen en correcties van gebruikers: onbekende manuscripten, geactualiseerde signaturen, links naar scans, transcripties, edities en geodata.

## Suggesties doorgeven

- **Per e-mail**: gebruik de link "Suggestie of correctie doorgeven" bij elk record op de website, of mail rechtstreeks. Vermeld het record-id en de bron van uw informatie.
- **Via GitHub**: open een issue in deze repository, of dien direct een pull request in met een aangepast of nieuw YAML-bestand (zie [DATAMODEL.md](DATAMODEL.md) voor de veldbeschrijving).

Alle inzendingen worden redactioneel beoordeeld voordat ze worden opgenomen.

## Werkwijze voor de redactie

1. Bewerk of maak de YAML-bestanden in `data/`.
2. Controleer en bouw: `python3 scripts/bouw.py` (het script weigert te bouwen bij ontbrekende verplichte velden of verwijzingen naar niet-bestaande id's).
3. Bekijk het resultaat lokaal door `docs/index.html` in een browser te openen.
4. Commit de wijzigingen en zet de inhoud van `docs/` op de webserver (of publiceer via GitHub Pages).

## Richtlijnen

- Neem signaturen letterlijk over van de huidige beschrijving bij de instelling en noteer de controledatum in `laatst_gecontroleerd`.
- Verouderde signaturen of vindplaatsen uit oudere literatuur horen in `opmerkingen`, met bronvermelding.
- Zet `controle_nodig: true` bij alles wat nog niet bij de instelling zelf is geverifieerd.
- Transcripties en scans worden bij voorkeur gelinkt op hun oorspronkelijke plek (instelling, editiesite); alleen materiaal waarvan de rechten dat toelaten wordt in deze repository zelf opgenomen.
