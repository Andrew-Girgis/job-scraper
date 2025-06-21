# main.py  --------------------------------------------------------------
"""
Orchestrator for the LinkedIn job-tracker.

Usage
-----
1) Scrape explicit URLs:
   $ python main.py https://www.linkedin.com/jobs/view/4209... \
                    https://www.linkedin.com/jobs/search/?currentJobId=...
2) Or just copy-paste links into jobs_to_scrape.txt
   then run:
   $ python main.py
"""

from __future__ import annotations
import sys, time, random
from pathlib import Path
from typing import List
from scraper import make_driver, fetch_job, search_to_view
from db import upsert_job
from pprint import pprint


PASTE_FILE = Path("jobs_to_scrape.txt")   # change if you wish


# --------------------------------------------------------------------- #
#  helper: gather list of raw URLs                                      #
# --------------------------------------------------------------------- #
def collect_urls(cli_args: List[str]) -> List[str]:
    """Return a deduped list of URLs from CLI + paste file."""
    urls = [u.strip() for u in cli_args if u.strip()]
    if PASTE_FILE.exists():
        urls += [ln.strip() for ln in PASTE_FILE.read_text().splitlines() if ln.strip()]
        # clear the file so we don't double-scrape next run
        PASTE_FILE.write_text("")
    # simple de-dupe while preserving order
    seen, clean = set(), []
    for u in urls:
        if u not in seen:
            clean.append(u)
            seen.add(u)
    return clean


# --------------------------------------------------------------------- #
#  main                                                                 #
# --------------------------------------------------------------------- #
def main(raw_urls: List[str]):
    urls_view = []
    for u in raw_urls:
        job_link = u if "/jobs/view/" in u else search_to_view(u)
        if job_link:
            urls_view.append(job_link)
        else:
            print(f"⚠️  skipped (no jobId found): {u}")

    if not urls_view:
        print("No new URLs found. Exiting.")
        return

    driver = make_driver(headless=False)
    ok, failed = 0, 0

    for url in urls_view:
        try:
            doc = fetch_job(url, driver)
            upsert_job(doc)
            ok += 1
            print(f"✓ stored {doc['job_title'][:40]} > {doc['company']}")
        except Exception as e:
            failed += 1
            print(f"❌ {url}   reason: {e}")
        # polite delay
        time.sleep(random.uniform(1.5, 3.0))

    driver.quit()
    print(f"\nDone. Success: {ok}  |  Failed: {failed}")


# --------------------------------------------------------------------- #
if __name__ == "__main__":
    # sys.argv[1:] are any URLs passed on the command line
    raw_urls = collect_urls(sys.argv[1:])
    main(raw_urls)
