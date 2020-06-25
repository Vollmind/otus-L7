prod:
    apt-get update
    apt-get install -f python3-pip python3-dev libpq-dev postgresql postgresql-contrib
    pg_ctlcluster 11 main start
    su - postgres -c psql
    CREATE DATABASE lesson7;
    CREATE USER lesson7user WITH PASSWORD 'otuslesson7';
    ALTER ROLE lesson7user SET client_encoding TO 'utf8';
    ALTER ROLE lesson7user SET default_transaction_isolation TO 'read committed';
    ALTER ROLE lesson7user SET timezone TO 'UTC';
    ALTER USER lesson7user CREATEDB;
    GRANT ALL PRIVILEGES ON DATABASE lesson7 TO lesson7user;
    \q
    apt-get install -f pipenv
    cd ..
    pipenv install
    pipenv shell
    python manage.py makemigrations
    python manage.py migrate
    python manager.py runserver 0.0.0.0:80