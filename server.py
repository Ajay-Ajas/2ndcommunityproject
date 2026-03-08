from flask import Flask, jsonify, request, render_template
import joblib
import pandas as pd
import random
from datetime import datetime

app = Flask(__name__)


# -------------------------------------------------
# LOAD ML MODELS
# -------------------------------------------------

device_model = joblib.load("device_model.pkl")
fault_model = joblib.load("fault_model.pkl")

device_dataset = pd.read_csv("device_suggestion_dataset.csv")
issue_dataset = pd.read_csv("issue_knowledge_dataset.csv")


# -------------------------------------------------
# SYSTEM STORAGE
# -------------------------------------------------

home_devices = []
alerts_list = []
history_records = []

previous_current = 0
last_fault = "Normal"


# -------------------------------------------------
# SENSOR BUFFER (for hardware)
# -------------------------------------------------

sensor_buffer = {
    "current": 0,
    "voltage": 0,
    "temperature": 0
}

simulation_mode = True


# -------------------------------------------------
# FRONTEND ROUTES
# -------------------------------------------------

@app.route("/")
def install_page():
    return render_template("install.html")


@app.route("/dashboard")
def dashboard():
    return render_template("main.html")


@app.route("/devices")
def devices_page():
    return render_template("devices.html")


@app.route("/graph")
def graph_page():
    return render_template("graph.html")


@app.route("/condition")
def condition_page():
    return render_template("condition.html")


@app.route("/alerts-page")
def alerts_page():
    return render_template("alerts.html")


@app.route("/history-page")
def history_page():
    return render_template("history.html")


@app.route("/profile")
def profile_page():
    return render_template("profile.html")


# -------------------------------------------------
# DEVICE STATUS
# -------------------------------------------------

@app.route("/device-status")
def device_status():
    return jsonify({"status": "online"})


# -------------------------------------------------
# ELECTRICAL CURRENT CHECK
# -------------------------------------------------

@app.route("/check-current")
def check_current():

    if simulation_mode:
        current = round(random.uniform(0.5, 8), 2)
    else:
        current = sensor_buffer["current"]

    return jsonify({"current": current})


# -------------------------------------------------
# START MONITORING
# -------------------------------------------------

@app.route("/start-monitoring")
def start_monitoring():
    return jsonify({"status": "monitoring_started"})


# -------------------------------------------------
# DEVICE LIST FROM DATASET
# -------------------------------------------------

@app.route("/device-list")
def device_list():

    devices = list(device_dataset["device_type"].unique())

    return jsonify({"devices": devices})


# -------------------------------------------------
# SAVE USER SELECTED DEVICES
# -------------------------------------------------

@app.route("/save-devices", methods=["POST"])
def save_devices():

    global home_devices

    data = request.json
    home_devices = data["devices"]

    return jsonify({
        "status": "devices_saved",
        "devices": home_devices
    })


# -------------------------------------------------
# GET SELECTED DEVICES
# -------------------------------------------------

@app.route("/get-devices")
def get_devices():
    return jsonify({"devices": home_devices})


# -------------------------------------------------
# DEVICE CONDITION LIST
# -------------------------------------------------

@app.route("/device-status-list")
def device_status_list():

    result = []

    for dev in home_devices:

        state = random.choice(["RUNNING", "OFF"])

        result.append({
            "name": dev,
            "condition": state
        })

    return jsonify({"devices": result})


# -------------------------------------------------
# LIVE ML MONITORING
# -------------------------------------------------

@app.route("/live-data")
def live_data():

    global previous_current
    global last_fault

    # ---------------------------------------------
    # DATA SOURCE
    # ---------------------------------------------

    if simulation_mode:

        avg_current = round(random.uniform(0.5, 6), 2)
        peak_current = avg_current + random.uniform(0.2, 2)

    else:

        avg_current = sensor_buffer["current"]
        peak_current = avg_current + 0.5


    # ---------------------------------------------
    # SIMULATED ELECTRICAL LINES
    # ---------------------------------------------

    wiring_line = random.choice(["L1", "L2", "L3"])


    # ---------------------------------------------
    # FEATURE EXTRACTION
    # ---------------------------------------------

    duty_cycle = random.uniform(0.2, 0.9)
    onoff_rate = random.randint(1, 10)
    usage_duration = random.randint(10, 120)


    # ---------------------------------------------
    # DEVICE PREDICTION
    # ---------------------------------------------

    device = device_model.predict([[
        avg_current,
        peak_current,
        duty_cycle,
        onoff_rate,
        usage_duration
    ]])[0]


    # ---------------------------------------------
    # DEVICE ON/OFF DETECTION
    # ---------------------------------------------

    if avg_current > previous_current + 1:
        device_state = "ON"
    elif avg_current < previous_current - 1:
        device_state = "OFF"
    else:
        device_state = "RUNNING"

    previous_current = avg_current


    # ---------------------------------------------
    # FAULT PREDICTION
    # ---------------------------------------------

    fault = fault_model.predict([[
        avg_current,
        avg_current,
        random.uniform(0, 1),
        random.uniform(0, 0.5),
        random.randint(0, 5),
        random.randint(0, 10),
        duty_cycle,
        random.uniform(30, 70)
    ]])[0]


    # ---------------------------------------------
    # ALERT GENERATION (avoid duplicates)
    # ---------------------------------------------

    alert_message = None

    if fault != "Normal" and fault != last_fault:

        match = issue_dataset[issue_dataset["ml_label"] == fault]

        if not match.empty:

            alert_message = match.iloc[0]["user_message"]

            alerts_list.append({
                "message": alert_message,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

            history_records.append({
                "message": alert_message,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    last_fault = fault


    # ---------------------------------------------
    # RESPONSE
    # ---------------------------------------------

    return jsonify({

        "current": avg_current,
        "device": device,
        "device_state": device_state,
        "wiring_line": wiring_line,
        "condition": fault,
        "alert": alert_message

    })


# -------------------------------------------------
# ALERTS API
# -------------------------------------------------

@app.route("/alerts")
def alerts():
    return jsonify({"alerts": alerts_list[::-1][:10]})


# -------------------------------------------------
# HISTORY API
# -------------------------------------------------

@app.route("/history")
def history():
    return jsonify({"records": history_records[::-1]})


# -------------------------------------------------
# HARDWARE SENSOR INPUT
# -------------------------------------------------

@app.route("/sensor-data", methods=["POST"])
def sensor_data():

    global sensor_buffer

    data = request.json

    sensor_buffer["current"] = data.get("current", 0)
    sensor_buffer["voltage"] = data.get("voltage", 0)
    sensor_buffer["temperature"] = data.get("temperature", 0)

    return jsonify({"status": "sensor data received"})


# -------------------------------------------------

app.run(host="0.0.0.0", port=5000, debug=True)