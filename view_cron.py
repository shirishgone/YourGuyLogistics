import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'

from apscheduler.schedulers.background import BackgroundScheduler

import requests
import base64
import json
from pytz import utc
from server import settings

scheduler = BackgroundScheduler(timezone=utc)

def base_url():
    if settings.ENVIRONMENT == 'PRODUCTION':
        url = 'http://yourguy.herokuapp.com/'
    elif settings.ENVIRONMENT == 'STAGE':
        url = 'http://yourguytestserver.herokuapp.com'
    else:
        url = 'http://127.0.0.1:8000'
    return url

def assign_dg():
    try:
        url = base_url() 
        url = url + '/api/v3/assign_dg/'
        result = requests.get(url)
    except:
        print('Error in Auto Assign')    

# AUTO ASSIGNED SCHEDULER ----------------------------------------
@scheduler.scheduled_job('cron', id='auto_assign_job_1', hour=0)
def auto_assign1():
    assign_dg()

@scheduler.scheduled_job('cron', id='auto_assign_job_2', hour=4)
def auto_assign2():
    assign_dg()

@scheduler.scheduled_job('cron', id='auto_assign_job_3', hour=6)
def auto_assign3():
    assign_dg()

@scheduler.scheduled_job('cron', id='auto_assign_job_4', hour=8)
def auto_assign4():
    assign_dg()

@scheduler.scheduled_job('cron', id='auto_assign_job_5', hour=11)
def auto_assign5():
    assign_dg()

# ----------------------------------------------------------------

# REPORTING SCHEDULER --------------------------------------------
@scheduler.scheduled_job('cron', id='daily_report_job', hour=17)
def daily_report():
    try:
        url = base_url() 
        url = url + '/api/v3/daily_report/'
        result = requests.get(url)
    except:
        print('send_daily_report : ERROR')


@scheduler.scheduled_job('cron', id='cod_report_job', hour=18)
def cod_report():
    try:
        url = base_url()
        url = url + '/api/v3/cod_report/'
        result = requests.get(url)
    except:
        print('send_cod_report : ERROR')


@scheduler.scheduled_job('cron', id='dg_report_job', hour=18)
def dg_report():
    try:
        url = base_url()
        url = url + '/api/v3/dg_report/'
        result = requests.get(url)
    except:
        print('send_dg_report : ERROR')

# ----------------------------------------------------------------
scheduler.start()

while True:
    pass
