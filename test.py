from pprint import pprint
from scraper import make_driver, fetch_job
from site_converter import search_to_view

url = "https://www.linkedin.com/jobs/view/4217878924/?trackingId=jugM%2FXsNWi7%2FRA7e20jnTw%3D%3D&refId=ByteString%28length%3D16%2Cbytes%3D5dbe482b...0c056b69%29&midToken=AQHYpHvj-4Vxig&midSig=39mqGA4TXU1rM1&trk=eml-email_job_alert_digest_01-job_card-0-job_posting&trkEmail=eml-email_job_alert_digest_01-job_card-0-job_posting-null-cb687o~ma35wtsr~n1-null-null&eid=cb687o-ma35wtsr-n1&otpToken=MTUwMTFhZTMxNDJlY2RjMmJjMjQwNGVkNDIxYmVlYjM4ZmM5ZDc0NDlkYTY4ZDYxNzdjNDA0NmI0NzUyNTRmYWY0ZGRkZjk5NThkMWJlZTM0NTlmZTI1N2RmMDY0NWI0OTU0MzM1YTMwNmFkMDExYTQxM2VlNywxLDE%3D"   # any public job link

driver = make_driver(headless=True)   # headless=True once things work

job_url = search_to_view(url)
if job_url:
    doc = fetch_job(job_url, driver)

driver.quit()
pprint(doc, depth=2, width=120)
