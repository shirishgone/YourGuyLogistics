import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'

from api_v3.report import daily_report, cod_report, dg_report, vendor_report
from api_v3.cron_jobs import assign_dg, notify_unassigned_deliveries, notify_delivery_delay
from celery.schedules import crontab
from celery.task import periodic_task


@periodic_task(run_every=(crontab(minute=0, hour=17)), name="dailyreport")
def dailyreport_task():
    daily_report()


@periodic_task(run_every=(crontab(minute=0, hour=17)), name="codreport")
def cod_task():
    cod_report()


@periodic_task(run_every=(crontab(minute=0, hour=17)), name="dgreport")
def dg_task():
    dg_report()


@periodic_task(run_every=(crontab(minute=0, hour=17)), name="vendorreport")
def vendor_task():
    vendor_report()


@periodic_task(run_every=(crontab(minute=0, hour='0, 4, 6, 8, 11')), name="assigndg")
def assign_dg_task():
    assign_dg()

@periodic_task(run_every=(crontab(minute='*/30')), name="notify_unassigned_deliveries")
def notify_unassigned_deliveries_task():
    notify_unassigned_deliveries()

@periodic_task(run_every=(crontab(minute='*/10')), name="notify_delivery_delay")
def notify_delivery_delay_task():
    notify_delivery_delay()