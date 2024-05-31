from flask import Flask, request, jsonify, render_template
import os
import sys
from datetime import datetime, timezone, timedelta
import requests

from dotenv import load_dotenv
load_dotenv()

FREECLIMB_URL = os.environ.get("LUMENCCS_URL", "api.lumenccs.com")
FREECLIMB_WEBRTC_URL = os.environ.get("LUMENCCS_WEBRTC_URL", "webrtc.lumenccs.com")
FREECLIMB_API_KEY = os.environ.get("LUMENCCS_API_KEY")
FREECLIMB_ACCOUNT_ID = os.environ.get("LUMENCCS_ACCOUNT_ID")
FREECLIMB_NUMBERS = os.environ.get("LUMENCCS_NUMBERS")
FREECLIMB_FLASK_SECRET = os.environ.get("LUMENCCS_FLASK_SECRET", "for_production_set_to_something_secure")


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

    return jsonify({"token": r1.text})

# Frontend Serving with config from env
@app.route("/webrtc-calls", methods=["GET"])
def webrtc_calls():
    return render_template('webrtc-calls.html', numbers=PARSED_FREECLIMB_NUMBERS.items(), domain=FREECLIMB_WEBRTC_URL)