import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'

from api_v3.report import daily_report, cod_report, dg_report,vendor_report
from api_v3.cron_jobs import assign_dg

from celery.schedules import crontab
from celery.task import periodic_task

from datetime import datetime

import dateutil.relativedelta
from django.db.models import Q
from rest_framework import status
from rest_framework.response import Response

from api_v3 import constants
from api_v3.utils import ist_day_start, ist_day_end, send_email
from yourguy.models import OrderDeliveryStatus


@periodic_task(run_every=(crontab(minute=0, hour=17)), name="dailyreport")
def dailyreport_task():
    daily_report()


@periodic_task(run_every=(crontab(minute=0, hour=18)), name="codreport")
def cod_task():
    cod_report()


@periodic_task(run_every=(crontab(minute=0, hour=18)), name="dgreport")
def dg_task():
    dg_report()


@periodic_task(run_every=(crontab(minute=10, hour=18)), name="vendorreport")
def vendor_task():
    vendor_report()


@periodic_task(run_every=(crontab(minute=10, hour='0, 4, 6, 8, 11')), name="assigndg")
def assign_dg_task():
    assign_dg()
