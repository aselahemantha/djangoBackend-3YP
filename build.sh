#!/usr/bin/env bash
set -o errexit

# Assuming the script is in the root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment
source "${SCRIPT_DIR}/venv/bin/activate"

# Install requirements
pip install -r "${SCRIPT_DIR}/requirements.txt"

# Run migrations
python "${SCRIPT_DIR}/manage.py" migrate

# Collect static files
python "${SCRIPT_DIR}/manage.py" collectstatic --no-input
