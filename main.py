from flask import Flask, request, jsonify, render_template
import os
import sys
from datetime import datetime, timezone, timedelta
import requests

from dotenv import load_dotenv
load_dotenv()

FREECLIMB_URL = os.environ.get("FREECLIMB_URL", "freeclimb.com")
FREECLIMB_WEBRTC_URL = os.environ.get("FREECLIMB_WEBRTC_URL", "webrtc.freeclimb.com")
FREECLIMB_API_KEY = os.environ.get("FREECLIMB_API_KEY")
FREECLIMB_ACCOUNT_ID = os.environ.get("FREECLIMB_ACCOUNT_ID")
FREECLIMB_NUMBERS = os.environ.get("FREECLIMB_NUMBERS")
FREECLIMB_FLASK_SECRET = os.environ.get("FREECLIMB_FLASK_SECRET", "for_production_set_to_something_secure")


if not FREECLIMB_ACCOUNT_ID or not FREECLIMB_API_KEY or not FREECLIMB_NUMBERS or not FREECLIMB_WEBRTC_URL:
    print("Please ensure required environment variables are set in the .env file")
    sys.exit(1)

PARSED_FREECLIMB_NUMBERS = {num.split(":")[0]:num.split(":")[1] for num in FREECLIMB_NUMBERS.split(",")}

app = Flask(__name__, static_url_path='')
app.secret_key = FREECLIMB_FLASK_SECRET

# FreeClimb JWT issuance via JWT API
@app.route("/auth/jwt", methods=["POST"])
def gen_jwt():
    body = request.json
    print(body)
    print(f"Using {FREECLIMB_URL}")
    exp = datetime.now(tz=timezone.utc) + timedelta(hours=1)
    r1 = requests.post(f"https://{FREECLIMB_URL}/apiserver/Accounts/{FREECLIMB_ACCOUNT_ID}/Calls/WebRTC/Token", auth=(FREECLIMB_ACCOUNT_ID, FREECLIMB_API_KEY), json={
        "to": str(body.get("to")),
        "from": str(body.get("from")),
        "uses": 10
    })

    if r1.status_code == 200:
        return jsonify({"token": r1.text})
    else:
        return jsonify({"error": "failed to fetch JWT from FreeClimb API"}),401

# Frontend Serving with config from env
@app.route("/webrtc-calls", methods=["GET"])
def webrtc_calls():
    application_list = requests.get(f"https://{FREECLIMB_URL}/apiserver/Accounts/{FREECLIMB_ACCOUNT_ID}/Applications", auth=(FREECLIMB_ACCOUNT_ID, FREECLIMB_API_KEY))
    number_list = requests.get(f"https://{FREECLIMB_URL}/apiserver/Accounts/{FREECLIMB_ACCOUNT_ID}/IncomingPhoneNumbers?hasApplication=true", auth=(FREECLIMB_ACCOUNT_ID, FREECLIMB_API_KEY))

    apps_with_numbers = []
    if application_list.status_code != 200 or number_list.status_code != 200:
        print("Failed to look up applications")
    else:
        apps = application_list.json().get("applications", [])
        for number in number_list.json().get("incomingPhoneNumbers", []):
            app_id = number.get("applicationId")
            if app_obj := [app for app in apps if app.get("applicationId") == app_id]:
                alias = app_obj[0].get("alias") if app_obj[0].get("alias") else app_obj[0].get("applicationId")
                apps_with_numbers.append((alias, number.get("phoneNumber")))

    return render_template('webrtc-calls.html', fc_applications=apps_with_numbers, numbers=PARSED_FREECLIMB_NUMBERS.items(), domain=FREECLIMB_WEBRTC_URL)