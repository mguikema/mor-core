#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo Collecting static files
python manage.py collectstatic --no-input

echo Apply migrations
python manage.py migrate --noinput

echo Create superuser
python manage.py createsuperuser --noinput || true

chmod -R ugo+rwx /srv/web/var/cache

chmod -R 777 /static

# exec uwsgi --ini /app/deploy/config.ini
exec python -m debugpy --listen 0.0.0.0:5678 /app/manage.py runserver 0.0.0.0:8000
