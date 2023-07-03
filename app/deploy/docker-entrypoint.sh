#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

# echo "Start with a fresh database"
# export PGPASSWORD=${DATABASE_PASSWORD}
# psql -h ${DATABASE_HOST_OVERRIDE} -p 5432 -d ${DATABASE_NAME} -U ${DATABASE_USER} -c "drop schema public cascade;"
# psql -h ${DATABASE_HOST_OVERRIDE} -p 5432 -d ${DATABASE_NAME} -U ${DATABASE_USER} -c "create schema public;"

echo Apply migrations
python manage.py migrate --noinput

echo Collecting static files
python manage.py collectstatic --no-input

echo Load initial data
python manage.py loaddata initial_data

echo Create superuser
python manage.py createsuperuser --noinput || true

echo Create users
python manage.py createusers --noinput || true

celery -A config worker -l info -D
celery -A config beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler --detach
uwsgi --ini /app/deploy/config.ini --daemonize /app/uwsgi.log
tail -f /app/uwsgi.log
