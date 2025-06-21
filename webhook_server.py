# webhook_server.py
import queue, threading, datetime, time, traceback, functools
from flask import Flask, request, jsonify
from selenium.webdriver.chrome.webdriver import WebDriver as _Chrome

from scraper import fetch_job, make_driver, maybe_login
from site_converter import search_to_view
from db import upsert_job

app = Flask(__name__)

# ──────────────────────────────────────────────────
# ❶ In‐memory stats
# ──────────────────────────────────────────────────
stats = {
    "pending":    0,
    "completed":  0,
    "failed":     0,
    "current":    None,
    "start_time": None,
}

# monkey‐patch omitted for brevity…

driver = make_driver(headless=False)
maybe_login(driver)

task_q: queue.Queue[str] = queue.Queue()

def scrape_and_store(job_url: str):
    # dequeue → run
    stats["pending"] = max(0, stats["pending"] - 1)
    stats["start_time"] = datetime.datetime.utcnow()
    stats["current"]    = {"title": None, "company": None}

    try:
        doc = fetch_job(job_url, driver)
        stats["current"] = {
          "title":   doc.get("job_title",   "—"),
          "company": doc.get("company",     "—")
        }
        upsert_job(doc)
        stats["completed"] += 1

    except Exception:
        stats["failed"] += 1

    finally:
        stats["current"]    = None
        stats["start_time"] = None

def worker():
    while True:
        url = task_q.get()
        try:
            scrape_and_store(url)
        except Exception as e:
            print("❌ error on", url, "→", e)
        task_q.task_done()

threading.Thread(target=worker, daemon=True).start()

@app.post("/webhook")
def inbound():
    raw     = request.get_json(force=True).get("url","")
    job_url = raw if "/jobs/view/" in raw else search_to_view(raw)
    if not job_url:
        return jsonify({"status":"bad_url"}), 400
    stats["pending"] += 1
    task_q.put(job_url)
    return jsonify({"status":"queued","job_url":job_url})

@app.get("/status")
def status():
    """Return live queue metrics for the popup."""
    now = datetime.datetime.utcnow()

    # ---------- elapsed for current job ----------
    if stats["start_time"]:
        elapsed_s = int((now - stats["start_time"]).total_seconds())
        elapsed    = f"{elapsed_s}s"
        running    = 1
    else:
        elapsed = "0s"
        running = 0

    # ---------- rough ETA (very simple) ----------
    done_jobs = stats["completed"] or 1            # avoid divide-by-0
    avg_secs  = 5                                  # you can refine later
    eta_s     = avg_secs * stats["pending"]
    eta       = f"{eta_s}s"

    return jsonify({
        "pending":   stats["pending"],
        "running":   running,
        "completed": stats["completed"],
        "failed":    stats["failed"],
        "current":   stats["current"],
        "elapsed":   elapsed,
        "eta":       eta
    })

@app.get("/")
def index():
    return "<h3>Job-tracker webhook running ✔️</h3>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
