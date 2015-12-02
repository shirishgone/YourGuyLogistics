import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'server.settings'

from apscheduler.schedulers.background import BackgroundScheduler

import requests
import base64
import json
from pytz import utc

scheduler = BackgroundScheduler(timezone=utc)

# AUTO ASSIGNED SCHEDULER ----------------------------------------
@scheduler.scheduled_job('cron', id='auto_assign_job_1', hour=0)
def auto_assign1():
	url = 'http://yourguy.herokuapp.com/api/v2/cron/'
	try:
		result = requests.get(url)
	except:
		print 'Error in Auto Assign'
		# REPORT ERROR

@scheduler.scheduled_job('cron', id='auto_assign_job_2', hour=4)
def auto_assign2():
	url = 'http://yourguy.herokuapp.com/api/v2/cron/'
	try:
		result = requests.get(url)
	except:
		print 'Error in Auto Assign'
		# REPORT ERROR

@scheduler.scheduled_job('cron', id='auto_assign_job_3', hour=6)
def auto_assign3():
	url = 'http://yourguy.herokuapp.com/api/v2/cron/'
	try:
		result = requests.get(url)
	except:
		print 'Error in Auto Assign'
		# REPORT ERROR

@scheduler.scheduled_job('cron', id='auto_assign_job_4', hour=8)
def auto_assign4():
	url = 'http://yourguy.herokuapp.com/api/v2/cron/'
	try:
		result = requests.get(url)
	except:
		print 'Error in Auto Assign'
		# REPORT ERROR

@scheduler.scheduled_job('cron', id='auto_assign_job_5', hour=11)
def auto_assign5():
	url = 'http://yourguy.herokuapp.com/api/v2/cron/'
	try:
		result = requests.get(url)
	except:
		print 'Error in Auto Assign'
		# REPORT ERROR

# ----------------------------------------------------------------

# REPORTING SCHEDULER --------------------------------------------
@scheduler.scheduled_job('cron', id='daily_report_job_6', hour=17)
def daily_report():
	print 'send_daily_report'
	url = 'http://yourguy.herokuapp.com/api/v2/daily_report/'
	try:
		result = requests.get(url)
	except:
		print 'send_daily_report : ERROR'
		# REPORT ERROR
# ----------------------------------------------------------------

scheduler.start()

while True:
	pass
