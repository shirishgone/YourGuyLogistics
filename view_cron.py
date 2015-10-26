import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'

from apscheduler.schedulers.background import BackgroundScheduler

import requests
import base64
import json
from pytz import utc

scheduler = BackgroundScheduler(timezone=utc)

# AUTO ASSIGNED SCHEDULER ----------------------------------------
def run_cron_assign_dg():
	print('run_cron_assign_dg method is called.')
	url = 'http://yourguy.herokuapp.com/api/v2/cron/'
	try:
		result = requests.get(url)
		print "Calling CRON JOB"
	except:
		print "Calling CRON JOB except case"



@scheduler.scheduled_job('cron', hour = 0)
def scheduled_job():
	print('Scheduled job.')
	run_cron_assign_dg()
# ----------------------------------------------------------------

# REPORTING SCHEDULER --------------------------------------------
def send_daily_report():
	url = 'http://yourguy.herokuapp.com/api/v2/daily_report/'
	try:
		result = requests.get(url)
	except:
		print "Error running CRON JOB Daily report"

@scheduler.scheduled_job('reporting_cron', hour = 16)
def scheduled_job_reporting():
	send_daily_report()
# ----------------------------------------------------------------

scheduler.start()
print('Scheduler started.')

while True:
    pass
