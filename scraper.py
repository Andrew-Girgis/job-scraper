"""
scraper.py
-----------
High-level helpers that turn a LinkedIn job URL into a clean Python
`dict` ready for cheap-first parsing, optional LLM enrichment, and
MongoDB insertion.
"""

# ──────────────────────────────────────────────────────────────────────
# 0️⃣ Future import MUST come first (after the docstring)
# ──────────────────────────────────────────────────────────────────────
from __future__ import annotations

# ──────────────────────────────────────────────────────────────────────
# 1️⃣ Monkey-patch Selenium’s WebDriver BEFORE any drivers are created
# ──────────────────────────────────────────────────────────────────────
import traceback
from selenium.webdriver.remote.webdriver import WebDriver as _WD
from selenium.webdriver.remote.command import Command

# Disable back/forward so we never return to the feed
_WD.back    = lambda self: None
_WD.forward = lambda self: None

# Wrap execute() to log navigation commands
_orig_execute = _WD.execute
def _traced_execute(self, driver_command, params=None):
    nav_cmds = {
        Command.GET,
        Command.GO_BACK,
        Command.REFRESH,
        Command.GO_FORWARD,
    }
    if driver_command in nav_cmds:
        print(f"\n▶ EXECUTE {driver_command!r}  params={params!r}")
        traceback.print_stack(limit=5)
    return _orig_execute(self, driver_command, params)
_WD.execute = _traced_execute

# Wrap get() to log every page load
_orig_get = _WD.get
def _traced_get(self, url):
    print(f"\n▶ driver.get({url!r})")
    traceback.print_stack(limit=5)
    return _orig_get(self, url)
_WD.get = _traced_get

# ──────────────────────────────────────────────────────────────────────
# 2️⃣ Now all your normal imports
# ──────────────────────────────────────────────────────────────────────
import os, time, datetime, random
from pathlib import Path
from typing import Dict, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from linkedin_scraper import Job as LinkedInJob, actions
from cheap_extract import cheap_extract
from post_process import post_process, set_currency_code
from llm_extract import extract_required_skills
import asyncio
from dotenv import load_dotenv; load_dotenv()


webdriver.back    = lambda self: None
webdriver.forward = lambda self: None

# ------------------------------------------------------------------------------
# 1.  DRIVER FACTORY
# ------------------------------------------------------------------------------

def make_driver(headless: bool = False,
                implicit_wait: int = 5) -> webdriver.Chrome:
    """Return a configured Chrome WebDriver."""
    opts = webdriver.ChromeOptions()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--log-level=3")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=opts
    )
    driver.implicitly_wait(implicit_wait)
    return driver


# ------------------------------------------------------------------------------
# 2.  LOGIN (once per driver session)
# ------------------------------------------------------------------------------

def maybe_login(driver):
    """Log in with environment-variable creds if not already signed in."""

    email    = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    if not email or not password:
        raise RuntimeError("Set LINKEDIN_EMAIL / LINKEDIN_PASSWORD env vars")

    actions.login(driver, email, password)      # library helper :contentReference[oaicite:0]{index=0}
    time.sleep(random.uniform(2, 3.5))          # human-like pause


# ------------------------------------------------------------------------------
# 3.  CORE FETCH
# ------------------------------------------------------------------------------

def fetch_job(url: str,
              driver: webdriver.Chrome,
              logged_in: bool = True,
              run_cheap_pass: bool = True) -> Dict:
    """
    Scrape one LinkedIn job posting …
    """

    # ——————————— New: always navigate straight to the job URL ———————————
    if logged_in:
        # refresh / load the job page under your authenticated session
        driver.get(url)
    else:
        driver.get(url)  # same for anonymous
    # ————————————————————————————————————————————————————————————————

    #maybe_login(driver) if logged_in else None

    job = LinkedInJob(
        url,
        driver              = driver,
        close_on_complete   = False,
        scrape              = False
    )

    # Call whichever scrape method is safest for you
    if logged_in:
        job.scrape_logged_in()         # uses your session cookie
    else:
        job.scrape()                   # anonymous scrape

    doc = job.to_dict()                # already flattens → dict
    #doc["scraped_at"] = datetime.datetime.utcnow()

    # Cheap pass (regex / spaCy) BEFORE we consider tokens
    if run_cheap_pass and "job_description" in doc:
        doc.update(cheap_extract(doc["job_description"]))

    doc = post_process(doc)
    set_currency_code(doc)

    # if 'required_skills' still missing → call LLM
    if not doc.get("required_skills"):
        skills = asyncio.run(extract_required_skills(doc["job_description"]))
        if skills:
            doc["required_skills"] = sorted(set(skills))


    return doc

# ------------------------------------------------------------------------------
# 4.  BATCH HELPER
# ------------------------------------------------------------------------------

def fetch_jobs_bulk(urls: list[str], headless: bool = False) -> list[Dict]:
    """Scrape many URLs with one browser session (faster & friendlier)."""
    driver = make_driver(headless=headless)
    docs   = []
    try:
        for u in urls:
            try:
                docs.append(fetch_job(u, driver))
                # Random jitter to reduce bot-detection risk
                time.sleep(random.uniform(1.5, 3.0))
            except Exception as e:
                print("⚠️  Error on", u, "->", e)
    finally:
        driver.quit()
    return docs


# ------------------------------------------------------------------------------
# 5.  LITTLE UTILITIES 
# ------------------------------------------------------------------------------

def save_raw_html(doc: Dict, out_dir: str | Path = "raw_pages"):
    """Dump the HTML snapshot for debugging / re-parsing later."""
    out_dir = Path(out_dir)
    out_dir.mkdir(exist_ok=True)
    fname = out_dir / f"{doc['linkedin_url'].split('/')[-2]}.html"
    fname.write_text(doc.get("html", ""), encoding="utf-8")
