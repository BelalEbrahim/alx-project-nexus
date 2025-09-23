web: gunicorn ecommerce.wsgi --log-file -
worker: celery -A ecommerce worker -l info --pool=gevent