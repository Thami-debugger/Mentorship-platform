#!/usr/bin/env bash
set -e

python -m pip install -r requirements.txt --target ./vendor
export PYTHONPATH=./vendor

# Create tables on startup (safe if they already exist)
python -c "from app import create_app, db; app=create_app(); app.app_context().push(); db.create_all(); print('db-ready')"

python run.py
