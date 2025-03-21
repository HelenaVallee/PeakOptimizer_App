import time
import csv
import os
import logging
import sys
import shutil
from datetime import datetime
from flask import Flask, render_template, jsonify, request
import threading
import json
from agents import RecommendActions

app = Flask(__name__)

# Create results directory if it doesn't exist, or delete and recreate it
if os.path.exists("results"):
    shutil.rmtree("results")  # Delete the entire results folder
os.makedirs("results", exist_ok=True)

# Set up logging
logging.basicConfig(
    filename="results/activity_log.csv", level=logging.INFO, format="%(message)s"
)

# CSV Headers
with open("results/activity_log.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Timestamp", "Event", "Details"])

# Global variables to store recent events for display
recent_events = []
MAX_EVENTS = 100  # Maximum number of events to store in memory

# Create a RecommendActions instance
recommend_agent = RecommendActions()


# Function to get active window title
def get_active_window():
    try:
        if os.name == "nt":  # Windows
            import win32gui

            window = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(window)
        elif os.name == "posix":  # macOS/Linux
            import subprocess

            if "Darwin" in os.uname().sysname:  # macOS
                result = subprocess.run(
                    [
                        "osascript",
                        "-e",
                        'tell application "System Events" to get name of (processes whose frontmost is true)',
                    ],
                    capture_output=True,
                    text=True,
                )
                return result.stdout.strip()
            else:  # Linux (X11-based)
                result = subprocess.run(
                    ["xdotool", "getwindowfocus", "getwindowname"],
                    capture_output=True,
                    text=True,
                )
                return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


# Track keyboard activity
def on_key_press(key):
    try:
        key_str = key.char if hasattr(key, "char") else str(key)
        log_event("KeyPress", key_str)
    except Exception as e:
        log_event("KeyPress", f"Error: {e}")


# Track mouse clicks
def on_click(x, y, button, pressed):
    action = "Pressed" if pressed else "Released"

    try:
        import screeninfo

        monitors = screeninfo.get_monitors()
        if monitors:
            primary = monitors[0]
            screen_info = f" (Screen: {primary.width}x{primary.height})"
        else:
            screen_info = ""
    except:
        screen_info = ""

    click_details = f"{button} {action} at coordinates ({x}, {y}){screen_info}"
    log_event("MouseClick", click_details)


# Log events to CSV and update recent events
def log_event(event, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log to CSV
    with open("results/activity_log.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, event, details])

    # Add to recent events for display
    recent_events.append({"timestamp": timestamp, "event": event, "details": details})

    # Keep only the most recent events
    while len(recent_events) > MAX_EVENTS:
        recent_events.pop(0)


# Track active application window changes
def monitor_active_window():
    last_window = None
    while True:
        active_window = get_active_window()
        if active_window and active_window != last_window:
            log_event("ActiveWindow", active_window)
            last_window = active_window
        time.sleep(2)


# Start tracking in background threads
def start_tracking():
    print(
        "Tracking keyboard, mouse, and active applications through the web interface..."
    )
    # Start the active window monitoring in a background thread
    window_thread = threading.Thread(target=monitor_active_window, daemon=True)
    window_thread.start()


# Flask routes
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/events")
def get_events():
    return jsonify(recent_events)


@app.route("/api/stats")
def get_stats():
    # Calculate some basic stats
    key_presses = sum(1 for event in recent_events if event["event"] == "KeyPress")
    mouse_clicks = sum(1 for event in recent_events if event["event"] == "MouseClick")
    window_changes = sum(
        1 for event in recent_events if event["event"] == "ActiveWindow"
    )

    return jsonify(
        {
            "key_presses": key_presses,
            "mouse_clicks": mouse_clicks,
            "window_changes": window_changes,
            "total_events": len(recent_events),
        }
    )


@app.route("/api/log_key", methods=["POST"])
def log_key():
    data = request.json
    if "key" in data:
        log_event("KeyPress", data["key"])
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No key provided"}), 400


@app.route("/api/log_mouse", methods=["POST"])
def log_mouse():
    data = request.json
    if "x" in data and "y" in data and "button" in data and "pressed" in data:
        action = "Pressed" if data["pressed"] else "Released"
        screen_info = f" (Screen: {data.get('screenWidth', 'unknown')}x{data.get('screenHeight', 'unknown')})"
        click_details = f"{data['button']} {action} at coordinates ({data['x']}, {data['y']}){screen_info}"
        log_event("MouseClick", click_details)
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Incomplete mouse data"}), 400


@app.route("/api/log_window", methods=["POST"])
def log_window():
    data = request.json
    if "window" in data:
        log_event("ActiveWindow", data["window"])
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "No window title provided"}), 400


@app.route("/api/recommend", methods=["POST"])
def get_recommendations():
    data = request.json
    if "events" in data:
        # Get the activity data from the request
        activity_data = data["events"]

        # Use the RecommendActions agent to generate recommendations
        recommendations = recommend_agent.generate_recommendations(activity_data)

        # Return the recommendations as HTML content
        return jsonify({"content": recommendations})

    return jsonify({"content": "No activity data available for recommendations"}), 400


if __name__ == "__main__":
    # Start tracking in background - just prints the informational message
    start_tracking()

    # Print the URL where the app will be available
    port = 7776
    print(f"\n* Running on http://127.0.0.1:{port}")
    print(f"* Running on http://localhost:{port}")
    print(f"* Also accessible on your network at http://0.0.0.0:{port}")
    print("* Press CTRL+C to quit\n")

    # Run Flask app
    app.run(debug=True, host="0.0.0.0", port=port)