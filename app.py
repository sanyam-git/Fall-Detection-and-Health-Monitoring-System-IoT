from flask import Flask,render_template,jsonify,request
import sqlite3
from utils import *
import json


app = Flask(__name__)


@app.route("/", methods=["GET"])
def main():
    return render_template("index.html")

@app.route("/get_data", methods=["GET","POST"])
def api():
    cur = db_connect()
    alpha = device_connection(cur)
    beta = heart_connection(cur)
    gamma = fall_connection(cur)
    delta = graph_connection(cur)

    payload = json.dumps({**alpha,**beta,**gamma,**delta})

    return payload

@app.route('/db_update',methods=['POST'])
def db_update():
    data = request.form.to_dict(flat=False)
    save_to_db(data['timestamp'][0],data['device_id'][0],data['is_fall'][0],data['heart_rate'][0])

    if int(data['is_sms'][0]):
        check_for_alert(data['sms_sender'][0],data['sms_reciever'][0],data['timestamp'][0],data['is_fall'][0],data['heart_rate'][0])

    return 'saved to database'