#!/usr/bin/env bash
# exit on error
set -o errexit

echo "Creating virtual environment..."
python3 -m venv .venv
echo "Virtual environment created."

echo "Activating virtual environment..."
. .venv/bin/activate
echo "Virtual environment activated."

echo "Collecting static files..."
python manage.py collectstatic --no-input
echo "Static files collected."

echo "Applying database migrations..."
python manage.py migrate
echo "Database migrations applied."

echo "Build script completed successfully."
