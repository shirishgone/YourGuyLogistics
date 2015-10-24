import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'

from apscheduler.schedulers.background import BackgroundScheduler

import requests
import base64
import json
from pytz import utc

scheduler = BackgroundScheduler(timezone=utc)

def run_cron_assign_dg():
	print('run_cron_assign_dg method is called.')
	url = 'http://yourguy.herokuapp.com/api/v2/cron/'
	try:
		result = requests.get(url)
		print "Calling CRON JOB"
	except:
		print "Calling CRON JOB except case"

# @scheduler.scheduled_job('interval', minutes = 1)
# def timed_job():
# 	print('This job is run every three minutes.')
	#run_cron_assign_dg()

@scheduler.scheduled_job('cron', hour = 0)
def scheduled_job():
	print('Scheduled job.')
	run_cron_assign_dg()

scheduler.start()
print('Scheduler started.')

while True:
    pass
