#!/usr/bin/env bash
set -o errexit

source venv/bin/activate

pip install -r requirements.txt

python manage.py migrate

python manage.py collectstatic --no-input
