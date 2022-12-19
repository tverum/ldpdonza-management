# Deployment

Dit document bevat de documentatie rond de deployment van ldpdonza-management.
De applicatie is een django-web applicatie, die gedeployd wordt met behulp van een gunicorn WSGI-server en een NGINX-reverse proxy.

## Locatie

De applicatie wordt gehost op het IP-adres 185.115.217.84.
Toegang krijgen tot deze server vereist het toevoegen van een public ssh-key aan ~/.ssh/known_hosts.

DNS wordt gehost door Dimitri, bij vragen moeten deze aan hem gesteld worden.

## Stack

De deployment gaat als volgt:

### Nginx

Nginx ontvangt de incoming requests op poort 443 en poort 80 (HTTP-requests worden automatisch doorgerouteerd naar HTTPS).
Nginx treedt op als reverse proxy, ontvangt de requests en stuurt deze door naar de gunicorn server.
Daarnaast gaat Nginx alle requests naar statische files cachen en zo sneller aanleveren.

De configuratie voor deze service kan gevonden worden in `/etc/nginx/sites-available/secretariaat.ldpdonza.be`
De logs kunnen gevonden worden in `/var/log/nginx/access.log` (access logs) en `/var/log/nginx/error.log` (error logs).

Om Nginx opnieuw op te starten gebruik je `sudo systemctl restart nginx`.

### Gunicorn

Gunicorn is een django WSGI-server.
Dit betekent dat deze server een wsgi-application neemt (geschreven in Django) en de requests hiernaar gaat verwerken.

De configuratie van gunicorn kan gevonden worden in de beschrijving van de gunicorn service.
In `/etc/systemd/system/gunicorn.service` vind je de configuratie hiervan.

De logs van gunicorn kan je raadplegen via `sudo systemctl status gunicorn` en `sudo journalctl -u gunicorn`
Gunicorn kan je opnieuw opstarten met behulp van de volgende commando's.

```bash
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```