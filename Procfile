web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn e commerce.wsgi:application --bind 0.0.0.0:8000
worker: celery -A e commerce worker -l info --pool=gevent