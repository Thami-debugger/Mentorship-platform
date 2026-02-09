#!/usr/bin/env bash
set -e

python -m pip install -r requirements.txt --target ./vendor
export PYTHONPATH=./vendor

# Load local env vars if present
if [ -f .env ]; then
	set -a
	. ./.env
	set +a
fi

# Create tables on startup (safe if they already exist)
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all(); print('db-ready')"

python run.py
