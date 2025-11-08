#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# If this repo contains a Django project, run collectstatic and migrations during the build.
if [ -f manage.py ]; then
	echo "manage.py found — running collectstatic and migrate"
	python manage.py collectstatic --noinput || { echo "manage.py collectstatic failed"; exit 1; }
	python manage.py migrate || { echo "manage.py migrate failed"; exit 1; }
else
	echo "manage.py not found — skipping Django build steps"
fi
