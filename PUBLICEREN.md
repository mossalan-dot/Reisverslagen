# De website publiceren

De website bestaat uit statische bestanden in `docs/` (`index.html` en `data.json`). Elke webserver kan die serveren; er is geen database of serverscript nodig. Na elke datawijziging: `python3 scripts/bouw.py` draaien en `docs/` opnieuw uploaden — of dat automatisch laten doen (route B).

## Route A — handmatig uploaden naar de eigen server

Eenmalig op de server (voorbeeld voor nginx op een Hetzner-VPS, met subdomein
`reisverslagen.<jouwdomein>.nl`):

1. Maak een map voor de site:
   ```
   sudo mkdir -p /var/www/reisverslagen
   ```
2. Voeg een serverblok toe, bijv. `/etc/nginx/sites-available/reisverslagen`:
   ```nginx
   server {
       listen 80;
       server_name reisverslagen.JOUWDOMEIN.nl;
       root /var/www/reisverslagen;
       index index.html;
   }
   ```
   Activeer en herlaad:
   ```
   sudo ln -s /etc/nginx/sites-available/reisverslagen /etc/nginx/sites-enabled/
   sudo nginx -t && sudo systemctl reload nginx
   ```
3. Zet bij je DNS-beheer (waar het domein staat) een A-record voor het
   subdomein naar het IP-adres van de server.
4. HTTPS met Let's Encrypt:
   ```
   sudo certbot --nginx -d reisverslagen.JOUWDOMEIN.nl
   ```

Daarna bij elke wijziging vanaf je eigen computer:
```
python3 scripts/bouw.py
rsync -av docs/ GEBRUIKER@SERVER:/var/www/reisverslagen/
```
(In plaats van een subdomein kan het ook in een submap van een bestaande site:
zet de inhoud van `docs/` dan in bijv. `/var/www/grisburgh/reisverslagen/`.)

Draait de server met Apache of een beheerpaneel (Plesk e.d.): upload de inhoud
van `docs/` via SFTP naar de webmap van het (sub)domein — meer is het niet.

## Route B — automatisch publiceren bij elke push (aanbevolen)

De workflow `.github/workflows/publiceer.yml` bouwt de site en zet `docs/` met
rsync op de server, telkens als er naar de hoofdbranch wordt gepusht. Eenmalige
inrichting:

1. Maak op je eigen computer een apart SSH-sleutelpaar voor deployment:
   ```
   ssh-keygen -t ed25519 -f deploysleutel -N "" -C "reisverslagen-deploy"
   ```
2. Zet de publieke sleutel op de server:
   ```
   ssh-copy-id -i deploysleutel.pub GEBRUIKER@SERVER
   ```
   (of plak de inhoud van `deploysleutel.pub` in `~/.ssh/authorized_keys`.)
3. Voeg in de GitHub-repository (Settings → Secrets and variables → Actions)
   vier *secrets* toe:
   | Naam | Waarde |
   |---|---|
   | `DEPLOY_HOST` | het IP-adres of de hostnaam van de server |
   | `DEPLOY_USER` | de SSH-gebruikersnaam |
   | `DEPLOY_PAD` | doelmap, bijv. `/var/www/reisverslagen/` |
   | `DEPLOY_SLEUTEL` | de inhoud van het *privé*-bestand `deploysleutel` |
4. Klaar. Elke push naar de hoofdbranch publiceert automatisch; onder
   "Actions" op GitHub zie je de logboeken. Zolang de secrets ontbreken slaat
   de workflow zichzelf over.

## Route C — GitHub Pages (geen eigen server nodig)

Settings → Pages → "Deploy from a branch", kies de hoofdbranch en de map
`/docs`. De site staat dan op `https://<gebruiker>.github.io/Reisverslagen/`;
een eigen (sub)domein is daar ook aan te koppelen. Handig als proefversie,
ook naast route A of B.
