web: gunicorn server.wsgi --log-file -
worker: python manage.py celery worker -B -l info