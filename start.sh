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

# Promote admin emails after tables exist
python -c "import os; from app import create_app, db; from app.models import User; app=create_app(); app.app_context().push(); emails=os.getenv('ADMIN_EMAILS') or os.getenv('ADMIN_EMAIL') or ''; admins={e.strip().lower() for e in emails.split(',') if e.strip()}; changed=False
for email in admins:
	user = User.query.filter_by(email=email).first()
	if user and user.role != 'admin':
		user.role = 'admin'
		changed = True
db.session.commit() if changed else None
print('admins-updated' if changed else 'admins-unchanged')"

python run.py
