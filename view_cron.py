import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'

from apscheduler.schedulers.background import BackgroundScheduler

import requests
import base64
import json
from pytz import utc

scheduler = BackgroundScheduler(timezone=utc)

def auto_assign_deliveries():
	url = 'http://yourguy.herokuapp.com/api/v2/cron/'
	try:
		result = requests.get(url)
	except:
		print 'Error in Auto Assign'
		# REPORT ERROR

# AUTO ASSIGNED SCHEDULER ----------------------------------------
@scheduler.scheduled_job('cron', id='auto_assign_job_id', hour=0)
def auto_assign():
	url = 'http://yourguy.herokuapp.com/api/v2/cron/'
	try:
		result = requests.get(url)
	except:
		print 'Error in Auto Assign'
		# REPORT ERROR
# ----------------------------------------------------------------

# REPORTING SCHEDULER --------------------------------------------
@scheduler.scheduled_job('cron', id='daily_report_job_id', hour=17)
def daily_report():
	print 'send_daily_report'
	url = 'http://yourguy.herokuapp.com/api/v2/daily_report/'
	try:
		result = requests.get(url)
	except:
		print 'send_daily_report : ERROR'
		# REPORT ERROR
# ----------------------------------------------------------------

scheduler.add_job(auto_assign_deliveries, id='auto_assign_job_1', hour=4)
scheduler.add_job(auto_assign_deliveries, id='auto_assign_job_2', hour=6)
scheduler.add_job(auto_assign_deliveries, id='auto_assign_job_3', hour=8)
scheduler.add_job(auto_assign_deliveries, id='auto_assign_job_4', hour=11)

scheduler.start()

while True:
	pass
