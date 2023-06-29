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

exec python -m debugpy --listen 0.0.0.0:5678 /app/manage.py runserver 0.0.0.0:8000
