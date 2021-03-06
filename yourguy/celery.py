# Module for creating celery instance

from __future__ import absolute_import

import os

from celery import Celery

os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'

from django.conf import settings

app = Celery('yourguy', broker = settings.BROKER_URL)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
