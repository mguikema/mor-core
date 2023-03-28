#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo Collecting static files
python manage.py collectstatic --no-input

# if [[ ${CLEAR_DATABSE_TABLES:-0} == 1 ]]; then
  echo "Start with a fresh database"
  export PGPASSWORD=${DATABASE_PASSWORD}
  psql -h ${DATABASE_HOST} -p 5432 -d ${DATABASE_NAME} -U ${DATABASE_USER} -c "drop schema public cascade;"
  psql -h ${DATABASE_HOST} -p 5432 -d ${DATABASE_NAME} -U ${DATABASE_USER} -c "create schema public;"
# fi

echo Apply migrations
python manage.py migrate --noinput

chmod -R ugo+rwx /srv/web/var/cache

chmod -R 777 /static

exec uwsgi --ini /app/deploy/config.ini
