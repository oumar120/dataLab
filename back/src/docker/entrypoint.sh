#!/bin/sh
set -e

if [ -n "$DJANGO_DB_PATH" ]; then
  mkdir -p "$(dirname "$DJANGO_DB_PATH")"
fi

# Database migrations (sqlite in volume)
python manage.py migrate --noinput

# Static files (served through proxy via /static/)
python manage.py collectstatic --noinput || true

exec gunicorn back.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 3 \
  --timeout 120
