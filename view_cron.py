import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'

from apscheduler.schedulers.background import BackgroundScheduler

import requests
import base64
import json
from pytz import utc

scheduler = BackgroundScheduler(timezone=utc)

# AUTO ASSIGNED SCHEDULER ----------------------------------------
def auto_assign_dgs():
	url = 'http://yourguy.herokuapp.com/api/v2/cron/'
	try:
		result = requests.get(url)
	except:
		# REPORT ERROR 

@scheduler.scheduled_job('cron', id = 'auto_assign', hour = 0)
def auto_assign():
	auto_assign_dgs()
# ----------------------------------------------------------------

# REPORTING SCHEDULER --------------------------------------------
def send_daily_report():
	print 'send_daily_report'
	url = 'http://yourguy.herokuapp.com/api/v2/daily_report/'
	try:
		result = requests.get(url)
	except:
		print 'send_daily_report : ERROR'
		# REPORT ERROR

@scheduler.scheduled_job('cron', id = 'daily_report', hour = 11)
def daily_report():
	print 'daily_report'
	send_daily_report()
# ----------------------------------------------------------------

scheduler.start()

while True:
    pass
