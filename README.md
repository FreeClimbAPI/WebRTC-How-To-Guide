# FreeClimb WebRTC Example

Example code and libraries to make a WebRTC enabled call through FreeClimb.

## How To

To run the example contained in this repository:

1. Ensure you have created the `.env` file from the `.env.example` with your FreeClimb details
2. Install python dependencies with `pip install -r requirements.txt`
    - optionally utilize a python virtual environment
        - `python3 -m venv venv`
        - `source venv/bin/activate`
        - `pip install -r requirements.txt`
3. Run the server with `FLASK_APP=main.py flask run --port 5001`
    - this is a development server, not for production use
4. Connect to `http://localhost:5001/webrtc-calls` via Google Chrome browser, this demo application has only been tested in Google Chrome.
5. Click on the desired call button
6. Hangup (if desired)

## SDK

The SDK, `whistle-engine.js`, provides primitives to interface with the [JsSIP Library](https://jssip.net/) in a convenient fashion, allowing for easy registration of callbacks and a simplified interface.

Example usage of the `whistle-engine.js` SDK:

```javascript
var config = {
    'user': '< FROM USER >',
    'domain': '< DOMAIN for USERS >',
    'proxy': '< SIP Gateway (often the same as domain) >',
    'port': 443,
    'authorization_jwt': `Bearer < JWT >`,

    // optional hooks to customize functionality
    'call_failed': function () {}
    'call_connected': function () {}
    'call_disconnected': function () {}
    'call_ended': function () {}
    'incoming_call': function () {}
};

engine = new WhistleEngine();
engine.start(config);
engine.dial("+1234567890");
```

## FreeClimb WebRTC Flow

```mermaid
sequenceDiagram
    actor eu as End User
    participant s as Customer Server
    participant ls as FreeClimb API Server
    participant lssm as FreeClimb WebRTC Media Gateway
    participant lsss as FreeClimb WebRTC SIP Gateway
    eu ->> s: End User connects to customer server to access webpage (HTTPS)
    s ->> eu: Customer Server provides webpage (HTTPS)
    eu ->> s: End User requests WebRTC call (HTTPS)
    s ->> ls: Customer Server requests JWT from FreeClimb API Server (HTTPS)
    ls ->> s: FreeClimb API Server provides JWT (HTTPS)
    s ->> eu: JWT is provided to End User Browser (HTTPS)
    eu ->> lsss: JWT Used in SIP Request to SIP Gateway (WSS)
    lsss ->> eu: SIP negotiation occurs to determine RTP Media Gateway (WSS)
    loop Until Call Completes
    eu ->> lssm: RTP is streamed to/from Media Gateway (WebRTC)
    end
```

## Structure of Example Application

This repo contains several components used to generate necessary authentication credentials as well as host a simple website used for demonstrating a WebRTC call.

| Object | Function |
| ------ | -------- |
| [static](./static/) | Both the underlying SIP library [JsSIP](./static/jssip-3.10.0.js) as well as the [SDK](./static/whistle-engine.js) |
| [templates](./templates/) | The sample HTML [document](./templates/webrtc-calls.html) that the [Flask](https://flask.palletsprojects.com/en/3.0.x/) application renders with the requested config|
| [main.py](./main.py) | This is the Python web application that will serve both the HTML document as well as interface with the FreeClimb API Server |
| [requirements.txt](./requirements.txt) | The list of required Python dependencies and versions, used for setup |
| [.env.example](./.env.example) | The example environment variables used to configure the Flask application |
| [Dockerfile](./Dockerfile) | The Dockerfile contains instructions for building the application as a Docker image as an alternate method of running |
