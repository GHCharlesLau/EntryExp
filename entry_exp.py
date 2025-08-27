from flask import Flask, redirect, request, jsonify
import random
import threading
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Target URLs
# URLS = [
#     "https://conversation-experiment.onrender.com/room/Room_1_pilot1",
#     "https://conversation-experiment-2.onrender.com/room/Room_2",
#     "https://conversation-experiment-3.onrender.com/room/Room_3",
#     "https://conversation-experiment-4.onrender.com/room/Room_4",
#     "https://conversation-experiment-5.onrender.com/room/Room_5",
# ]
URLS = [
    "https://conversation-experiment.onrender.com/join/pijemiri",
    "https://conversation-experiment-2.onrender.com/join/puropito",
]

# Count traffic for each URL
counts = [0] * len(URLS)
lock = threading.Lock()

# Log file
LOG_FILE = "logs.csv"

# Initialize log file
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["time", "ip", "user_agent", "url"])


def log_visit(ip, user_agent, url):
    """Record visit in CSV"""
    with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().isoformat(), ip, user_agent, url])

@app.route("/")
def index():
    """Home page"""
    return """
    <h1>Redirector</h1>
    <p>Redirect to a random URL.</p>
    <a href="/entry">Entry</a>
    <p><a href="/stats">Stats</a></p>
    """

@app.route("/entry")
def entry():
    global counts
    with lock:
        # Find a URL with the least traffic
        min_count = min(counts)
        candidates = [i for i, c in enumerate(counts) if c == min_count]
        chosen = random.choice(candidates)

        # Upate counts
        counts[chosen] += 1
        target_url = URLS[chosen]

    # Info of the user
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    user_agent = request.headers.get("User-Agent", "unknown")

    # Logging
    log_visit(ip, user_agent, target_url)

    # Redirect
    return redirect(target_url, code=302)


@app.route("/stats")
def stats():
    """Display stats"""
    stats_data = {
        "url_counts": {},
        "recent_logs": []
    }

    # URL Traffic（Memory data）
    for i, url in enumerate(URLS):
        stats_data["url_counts"][url] = counts[i]

    # Latest 100 logs
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode="r", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            stats_data["recent_logs"] = rows[-100:] if len(rows) > 100 else rows

    return jsonify(stats_data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
