from flask import Flask, render_template, request, jsonify, session
import requests
import pyrebase
from datetime import datetime
from pytz import timezone
import base64
import json

#UPDATE GROK URL SO THAT IMAGES ARE DISPLAYED
GROK_URL = "___"

fmt = '%Y-%m-%d %H:%M:%S %Z%z'
# define eastern timezone
eastern = timezone('US/Eastern')

config = {
  "apiKey": "___",
  "authDomain": "___",
  "databaseURL": "___",
  "storageBucket": "___m",
  "serviceAccount": "___"
}

# from twilio.twiml.messaging_response import MessagingResponse, Message
from twilio.rest import Client
import urllib

#Twilio config
# Your Account SID from twilio.com/console
account_sid = "____"
# Your Auth Token from twilio.com/console
auth_token  = "____"
client = Client(account_sid, auth_token)

firebase = pyrebase.initialize_app(config)

db = firebase.database()

app = Flask(__name__)

@app.route("/")
def index():
    images = db.child("images").get().val()
    alerts = db.child("alerts").get().val()
    return render_template("index.html", images=images, alerts=alerts)

@app.route("/heartrate")
def heartrate():
    heartrate = db.child("heartrate").get().val()
    return render_template("heartrate.html", heartrate=heartrate)

@app.route("/alerts")
def alerts():
    alerts = db.child("alerts").get().val()
    # print((alerts))
    images = db.child("images").get().val()
    # print((images))
    videos = db.child("videos").get().val()
    # print((videos))
    return render_template("alerts.html", alerts=alerts, images=images, videos=videos)

@app.route("/images")
def images():
    images = db.child("images").get().val()
    # print((alertrequest.get_json()))
    return render_template("images.html", images=images)

@app.route("/videos")
def videos():
    videos = db.child("videos").get().val()
    # print((alertrequest.get_json()))
    return render_template("videos.html", videos=videos)

@app.route("/alert", methods=['POST'])
def alert():
    print(request.data)
    dict_req = json.loads(request.data)

    patient_name = dict_req["patient_name"]
    patient_id = dict_req["patient_id"]

    from_number = "+18508765266"
    to_number = "+17812288105"

    message = client.messages.create(
        body="Alerting that patient: " + patient_name + " has fallen down",
        from_=from_number,
        to=to_number
    )

    loc_dt = datetime.now(eastern)
    current_date = loc_dt.strftime(fmt)

    data = {"reason": "fall", "patientID": patient_id, "patientName": patient_name, "date": current_date}
    db.child("alerts").push(data)

    # Post to Firebase
    return "Alert has been sent to first responders"


@app.route("/mms", methods=['POST'])
def mms():
    print(request.data)
    dict_req = json.loads(request.data)

    patient_name = dict_req["patient_name"]
    patient_id = dict_req["patient_id"]
    rgb64 = dict_req["rgb64"]
    # lidar64 = dict_req["lidar64"]

    # base64 image
    # name + date + .png
    loc_dt = datetime.now(eastern)
    current_date = loc_dt.strftime("%Y%m%d-%H%M%S")
    rgb_picture = "rgb" + current_date + "_" + patient_id + ".jpg"
    # lidar_picture = "lidar" + current_date + "_" + patient_id + ".jpg"

    # Images decoded correctly
    with open("static/" + rgb_picture, "wb") as fh:
        fh.write(base64.decodebytes(rgb64.encode()))
    fh.close()

    # with open("static/" + lidar_picture, "wb") as fh:
    #     fh.write(base64.decodebytes(lidar64.encode()))
    # fh.close()

    from_number = "+18508765266"
    to_number = "+17812288105"

    message = client.messages.create(
        body="Your patient: " + patient_name + " is hurt",
        from_=from_number,
        # media_url = [GROK_URL + "/static/" + rgb_picture, GROK_URL + "/static/" + lidar_picture],
        media_url = GROK_URL + "/static/" + rgb_picture,
        to=to_number
    )

    # print(GROK_URL + "/static/" + rgb_picture)
    # print(GROK_URL + "/static/" + lidar_picture)

    # data = { "patientID": patient_id, "patientName": patient_name, "lidar": lidar64, "rgb": rgb64, "rgb_url": rgb_picture, "lidar_url": lidar_picture, "date": current_date}
    data = { "patientID": patient_id, "patientName": patient_name, "rgb": rgb64, "rgb_url": rgb_picture, "date": current_date}
    db.child("images").push(data)

    # Post to Firebase
    return "MMS Message Posted Successfully"

@app.route("/video", methods=['POST'])
def video():
    print(request.data)
    dict_req = json.loads(request.data)
    patient_name = dict_req["patient_name"]
    video_link = dict_req["video_link"]
    patient_id = dict_req["patient_id"]

    # Grab the relevant phone numbers.
    from_number = "+18508765266"
    to_number = "+17812288105"

    message = client.messages.create(
        body="Patient " + patient_name + " video is here: " + video_link,
        from_=from_number,
        to=to_number
    )

    loc_dt = datetime.now(eastern)
    current_date = loc_dt.strftime(fmt)

    data = {"video_link": video_link, "patientID": patient_id, "patientName": patient_name, "date": current_date}
    db.child("videos").push(data)

    # Post to Firebase
    return "Video Link Posted Successfully"

@app.route("/fitbitAlert", methods=['POST'])
def fitbitAlert():
    dict_req = json.loads(request.data)
    patient_name = dict_req["patient_name"]
    patient_id = dict_req["patient_id"]
    alert = "Heart beat has fallen below 55 bpm or risen above 110 bpm"
    # from_number = request.form['from']
    # to_number = request.form['to']
    from_number = "+18508765266"
    to_number = "+17812288105"

    message = client.messages.create(
        body="Alerting that patient: " + patient_name + " heart beat is abnormal",
        from_=from_number,
        to=to_number
    )

    loc_dt = datetime.now(eastern)
    current_date = loc_dt.strftime(fmt)
    data = {"patientID": patient_id, "patientName": patient_name, "date": current_date}
    db.child("heartrate").push(data)

    # render popup window for elevated heartrate
    # in static/javascript.js
    return "Fitbit alert has been successfully sent"

@app.route("/fitbitStatus", methods=['GET'])
def fitbitStatus():
    if db.child("heartrate").get().val() != None:
        return str(1)
    else:
        return str(0)



# How do we reset
