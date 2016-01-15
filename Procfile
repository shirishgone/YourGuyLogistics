web: gunicorn server.wsgi --log-file -
clock: python view_cron.py
worker: python manage.py celery worker -B -l info