#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo "See if Postgres is up"
until PGPASSWORD=$DATABASE_PASSWORD psql  -d $DATABASE_NAME -h $DATABASE_HOST_OVERRIDE -U $DATABASE_USER -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done
echo "Postgres is up!"

echo Collecting static files
python manage.py collectstatic --no-input

echo Apply migrations
python manage.py migrate --noinput

echo Create superuser
python manage.py createsuperuser --noinput || true

chmod -R ugo+rwx /srv/web/var/cache

chmod -R 777 /static

echo Test python app
python manage.py test

# exec uwsgi --ini /app/deploy/config.ini
# exec python -m debugpy --listen 0.0.0.0:5678 /app/manage.py runserver 0.0.0.0:8000
