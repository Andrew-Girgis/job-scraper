# db.py
from __future__ import annotations
import os, datetime                       # ←  add datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from dotenv import load_dotenv; load_dotenv()

# ------------------------------------------------------------------
# 1) URI
# ------------------------------------------------------------------
MONGO_URI = os.getenv("MONGO_URI") or os.getenv("mongo_uri")
if not MONGO_URI:
    raise RuntimeError("Set MONGO_URI env var with your Atlas string")

# ------------------------------------------------------------------
# 2) client
# ------------------------------------------------------------------
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
client.admin.command("ping")
print("✓ MongoDB connection OK")

# ------------------------------------------------------------------
db      = client.get_database("jobtracker")
jobs: Collection = db.get_collection("jobs")
jobs.create_index("linkedin_url", unique=True)
jobs.create_index("posted_at")
jobs.create_index("city")
# (vector index commented out)

# ------------------------------------------------------------------
def upsert_job(doc: dict) -> None:
    """
    Insert or update one job.
    - keeps the *first* scraped_at timestamp
    - never writes scraped_at twice (no path-conflict)
    """
    first_seen = doc.pop("scraped_at", None) \
        or datetime.datetime.now(datetime.timezone.utc)

    jobs.update_one(
        {"linkedin_url": doc["linkedin_url"]},
        {"$set": doc,
         "$setOnInsert": {"scraped_at": first_seen}},
        upsert=True,
    )
