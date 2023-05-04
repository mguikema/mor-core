#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo Test python app
python manage.py test apps.meldingen.tests.tests_api
python manage.py test apps.meldingen.tests.tests_models
