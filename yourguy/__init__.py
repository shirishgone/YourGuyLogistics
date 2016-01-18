# To ensure app is loaded when Django starts

from __future__ import absolute_import
from .celery import app as celery_app
