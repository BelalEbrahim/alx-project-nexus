#!/bin/bash
set -e

# Only run for web service (command starts with gunicorn)
if [[ "$1" == "gunicorn" ]]; then
  python manage.py migrate
  python manage.py collectstatic --noinput
fi

# Execute the command (Gunicorn or Celery)
exec "$@"