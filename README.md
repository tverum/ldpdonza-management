# ldpdonza-management

Web app voor ledenbeheer van basketbal club LDPDonza

## Requirements

- python3.8 (`sudo apt -y install python3.8`)
- venv (`sudo apt -y install python3.8-venv`)
- mysql (`sudo apt-get -y install mysql-server libmysqlclient-dev`)
- wheel (`pip3 install wheel`)
- python3 development tools (`sudo apt-get -y install python3-dev`)
- python3-pip (`sudo apt-get -y install python3-pip`)
- docker
  - installation guide: https://docs.docker.com/engine/install/
  - if you're installing docker for the first time, have a look at https://docs.docker.com/engine/install/linux-postinstall/

## Set-up

De website is geschreven in Django, een Python webframework.

### Database

Voor de backend database wordt een mysql-database gebruikt.
Hiervoor moet er een database zijn met naam `ID309280_secretariaat`, een user django met wachtwoord django en die user moet alle privileges hebben op de database.
```sql
CREATE DATABASE ID309280_secretariaat;
CREATE USER 'django'@'localhost' IDENTIFIED BY 'django';
GRANT ALL PRIVILEGES ON ID309280_secretariaat.* TO 'django'@'localhost';
```

### Backend

De backend is een django webserver. De requirements hiervoor zijn te vinden in de root-folder.
Installeer de requirements in requirements.
```bash
python3 -m venv venv                    # create a virtual environment in the folder venv
source venv/bin/activate                # activate the virtual environment
python3 -m install -r requirements.txt  # install the requirements in the virtual environment
```

## Create superuser

To deploy the application locally, you need to make sure that you have a superuser present.
To create a superuser, execute the following command.

```bash
python manage.py createsuperuser
```

## Development Environment

Vooraleer de development server te runnen, moet je de lokale settings voor het project inladen.
```bash
mv donza/settings/local-copy.py donza/settings/local.py
```

Om de development server te runnen, ga lokaal naar de map `donza` en voer de volgende commando's uit:
```bash
docker run -p 6379:6379 -d redis:5      # start up the redis messaging channel
python manage.py makemigrations         # check for non-executed migrations that must be performed
python manage.py migrate                # migrate all unmigrated migrations
python manage.py runserver              # start up development server
```

Tadaaaa, you can start developing. The development server will update

## TODO:

- Add grant all privileges on TEST database for running tests.
