#!/bin/bash
set -e
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
mkdir -p staticfiles
python manage.py collectstatic --noinput
python manage.py migrate --noinput
python manage.py createsuperuser --noinput

