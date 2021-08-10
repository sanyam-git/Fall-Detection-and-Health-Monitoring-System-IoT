import json
import time
import sqlite3
from datetime import datetime
import pytz
from twilio.rest import Client
import os.path

DEVICE_CONNECTION_THRESHOLD = 65
HEART_CONNECTION_THRESHOLD = 65
HEART_RATE_THRESHOLD = 100

DATABASE_NAME = 'main_db'

def db_connect():
	# connect database
    database_name = DATABASE_NAME
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, database_name)
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    return cur

def time_convertor(last_timestamp):
	seconds = lag(last_timestamp)
	if seconds<60:
		return str(seconds)+' second(s)'
	elif seconds>=60 and seconds<3600:
		return str(seconds//60)+' minute(s)'
	elif seconds>=360 and seconds<86400:
		return str(seconds//3600)+' hour(s)'
	else:
		return str(seconds//86400)+' day(s)'

def beautify_time(last_timestamp):
	ist = pytz.timezone("Asia/Kolkata")
	data = datetime.fromtimestamp(last_timestamp, ist)
	txt = "({hour} : {minute} {am_or_pm}, {day} {month_name} {year})"
	txt = txt.format(hour = data.strftime('%I'), minute = data.minute, am_or_pm = data.strftime('%p'), day = data.day, month_name = data.strftime('%B'), year = data.year)
	return txt

def get_graph_time(last_timestamp):
	ist = pytz.timezone("Asia/Kolkata")
	data = datetime.fromtimestamp(last_timestamp, ist)
	return str(data.strftime('%I'))+' : '+str(data.minute)

def lag(last_timestamp):
	seconds = abs(int(time.time())-last_timestamp)
	return seconds

def device_connection(cur):
	payload = {}

	last_record = cur.execute("SELECT timestamp from MAIN order by serial_number DESC").fetchone()
	time_lag = lag(last_record[0])
	if time_lag < DEVICE_CONNECTION_THRESHOLD:	
		payload['alpha_one'] = 1
	else:
		payload['alpha_one'] = 0
	payload['alpha_delay'] = time_convertor(last_record[0])
	payload['alpha_time'] = beautify_time(last_record[0])	

	return payload

def heart_connection(cur):
	payload = {}

	last_record = cur.execute("SELECT timestamp, heart_rate from MAIN WHERE heart_rate>0 order by serial_number DESC").fetchone()
	average = cur.execute("SELECT AVG(heart_rate) FROM MAIN WHERE heart_rate>0").fetchone()
	time_lag = lag(last_record[0])
	if time_lag < HEART_CONNECTION_THRESHOLD:	
		payload['beta_one'] = 1
	else:
		payload['beta_one'] = 0
	payload['beta_delay'] = time_convertor(last_record[0])
	payload['beta_time'] = beautify_time(last_record[0])
	payload['beta_heart_rate'] = last_record[1]
	payload['beta_heart_average'] = int(average[0])
	return payload

def fall_connection(cur):
	payload = {}

	last_record = cur.execute("SELECT timestamp,heart_rate from MAIN WHERE is_fall=1 order by serial_number DESC").fetchone()
	
	if last_record==None:
		payload['gamma_exist'] = 0
	else:
		payload['gamma_exist'] = 1
		payload['gamma_delay'] = time_convertor(last_record[0])
		payload['gamma_time'] = beautify_time(last_record[0])
		payload['gamma_heart_rate'] = last_record[1]

	return payload

def graph_connection(cur):
	payload = {}
	#time_lag = int(time.time()-3700)
	#txt = "SELECT timestamp,heart_rate from MAIN WHERE timestamp>={kappa} order by serial_number DESC LIMIT 30"
	#txt = txt.format(kappa = time_lag)
	txt = "SELECT timestamp,heart_rate from MAIN WHERE heart_rate>=0 order by serial_number DESC LIMIT 30"
	last_hour = cur.execute(txt)
	labels = []
	data = []
	for record in last_hour:
		#labels.append(get_graph_time(record[0]))
		labels.append(beautify_time(record[0]).replace('(','').replace(')',''))
		#if record[1]>0:
		data.append(record[1])
		#else:
		#data.append(-1)
	labels.reverse()
	data.reverse()
	payload['delta_lables'] = labels
	payload['delta_data'] = data
	return payload

"""files for message reciever"""

def save_to_db(timestamp,device_id,is_fall,heart_rate):
	database_name = DATABASE_NAME
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	db_path = os.path.join(BASE_DIR, database_name)
	con = sqlite3.connect(db_path)
	cur = con.cursor()
	query = '''INSERT INTO MAIN (timestamp, device_id, is_fall, heart_rate) \
			VALUES ({timestamp},'{device_id}',{is_fall},{heart_rate})'''.format(timestamp = timestamp, 
				device_id=device_id, is_fall = is_fall, heart_rate = heart_rate)
	cur.execute(query)
	con.commit()

def check_for_alert(sms_sender, sms_reciever,timestamp_ep, is_fall, heart_rate):
	timestamp = beautify_time(timestamp_ep)

	if is_fall==1:
		body = "Fall Detected at {timestamp}. Heart Rate is {heart_rate} bpm."
		if heart_rate<0:
			heart_rate = '(sensor not connected)'
		message_body = body.format(timestamp = timestamp, heart_rate= heart_rate)
	elif heart_rate>=HEART_RATE_THRESHOLD:
		body = "Heart Rate crossed {threshold_value} bpm at {timestamp}, Current value is {heart_rate} bpm."
		if heart_rate<0:
			heart_rate = '(sensor not connected)'
		message_body = body.format(threshold_value = HEART_RATE_THRESHOLD,timestamp = timestamp, heart_rate= heart_rate)
	send_sms(message_body,sms_sender, sms_reciever)


def send_sms(body,sender,reciever):
	account_sid = 'AC081631eab85ec9c4c3db39bc8906c612'
	auth_token = '6b8eba0a2fb07c1aa93187c18a5ebe97'
	client = Client(account_sid, auth_token)

	message = client.messages \
	    .create(
	         body=body,
	         from_=sender,
	         to=reciever
	     )
	print("*****ALERTED BY SMS********")