# url_utils.py
from urllib.parse import urlparse, parse_qs
import re

def search_to_view(url: str) -> str | None:
    """
    Convert a LinkedIn jobs SEARCH url to a canonical /jobs/view/<id>/ url.
    Returns None if no job-ID parameter found.
    """
    if "/jobs/view/" in url:
        return url.split("?")[0].rstrip("/") + "/"
    
    parsed = urlparse(url)
    qs     = parse_qs(parsed.query)

    # Most common parameter names
    job_id = (
        qs.get("currentJobId", [None])[0] or
        qs.get("jobId",        [None])[0]
    )

    # Fallback: regex for 'currentJobId=123456789' anywhere in the string
    if job_id is None:
        m = re.search(r'(?:currentJobId|jobId)=(\d+)', url)
        if m:
            job_id = m.group(1)

    return f"https://www.linkedin.com/jobs/view/{job_id}/" if job_id else None


# CLI helper ---------------------------------------------------------------
if __name__ == "__main__":           # allow:  python url_utils.py <search-url>
    import sys
    if len(sys.argv) == 2:
        print(search_to_view(sys.argv[1]))
    else:
        print("usage: python url_utils.py <linkedin-search-url>")
