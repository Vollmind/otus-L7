prod:
	apt-get update
	apt-get -y install -f python3-pip python3-dev libpq-dev postgresql postgresql-contrib
	pg_ctlcluster 11 main start
	su - postgres -c "psql -c \"CREATE DATABASE lesson7\""
	su - postgres -c "psql -c \"CREATE USER lesson7user WITH PASSWORD 'otuslesson7'\""
	su - postgres -c "psql -c \"ALTER ROLE lesson7user SET client_encoding TO 'utf8'\""
	su - postgres -c "psql -c \"ALTER ROLE lesson7user SET default_transaction_isolation TO 'read committed'\""
	su - postgres -c "psql -c \"ALTER ROLE lesson7user SET timezone TO 'UTC'\""
	su - postgres -c "psql -c \"ALTER USER lesson7user CREATEDB\""
	su - postgres -c "psql -c \"GRANT ALL PRIVILEGES ON DATABASE lesson7 TO lesson7user\""
	apt-get -y install -f pipenv
	cd .. && pipenv install --system && python manage.py makemigrations && \
	python manage.py migrate && setsid python manager.py runserver 0.0.0.0:80 > ./log.log 2>&1 < /dev/null &
