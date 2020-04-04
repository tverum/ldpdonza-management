# ldpdonza-management

Web app voor ledenbeheer van basketbal club LDPDonza

## Set-up

De website is geschreven in Django, een Python webframework. Er wordt verondersteld dat je Python (en bijbehorend pip) geïnstalleerd hebt.

Installeer de requirements in requirements. Het wordt aangeraden om hiervoor een conda environment te gebruiken. Voor hulp bij de installatie daarvan zie [volgende link](https://docs.conda.io/projects/conda/en/latest/user-guide/install/).
Om de requirements te installeren, activeer een nieuwe conda omgeving met `python3.7` als python interpreter en voer dan het volgende commando uit:
```bash
pip install -r requirements.txt
```

Om de development server te runnen, ga lokaal naar de map `donza` en voer het volgende commando uit:
```bash
python manage.py runserver
```

Tadaaaa, you can start developing.
