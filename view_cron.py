import os
from server import settings

import requests
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc

os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'
scheduler = BackgroundScheduler(timezone=utc)
scheduler.start()

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

# ----------------------------------------------------------------
#
# while True:
#     pass
