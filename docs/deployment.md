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

### Gunicorn

Gunicorn is een django WSGI-server.
Dit betekent dat deze server een wsgi-application neemt (geschreven in Django) en de requests hiernaar gaat verwerken.

De configuratie van gunicorn kan gevonden worden in de project root in `/config/gunicorn/prod.py`. Configuratie is dus in python.
De logs van gunicorn kunnen gevonden worden in `/var/log/gunicorn/access.log` (accesss logs) en `/var/log/gunicorn/error.log` (error logs) op de server.