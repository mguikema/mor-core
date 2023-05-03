#!/usr/bin/env bash
set -u   # crash on missing env variables
set -e   # stop on any error
set -x

echo Test python app
python3 manage.py test apps.mor.tests.tests_api
python3 manage.py test apps.mor.tests.tests_models
