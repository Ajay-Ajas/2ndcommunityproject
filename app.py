from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

device = {
    "device_id": None,
    "status": "offline"
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/connect")
def connect():
    return render_template("connect.html")

@app.route("/install")
def install():
    return render_template("install.html")

@app.route("/register-device", methods=["POST"])
def register():

    data = request.json

    device["device_id"] = data["device_id"]
    device["status"] = "online"

    print("Device connected:", device)

    return jsonify({"ok": True})

@app.route("/device-status")
def status():
    return jsonify(device)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)e