#!/usr/bin/env bash
# exit on error
set -o errexit

python3 -m venv .venv
. .venv/bin/activate

python manage.py collectstatic --no-input
python manage.py migrate