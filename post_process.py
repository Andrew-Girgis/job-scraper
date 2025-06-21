

import re, dateparser
def post_process(doc):
    """Clean location string, posted date, applicant count, etc."""
    loc_raw = doc.get("location", "")
    parts   = [p.strip() for p in loc_raw.split("·")]
    if len(parts) >= 1 and "," in parts[0]:
        doc["city"], doc["province"] = map(str.strip, parts[0].split(",", 1))
    if len(parts) >= 2:
        doc["posted_at"] = dateparser.parse(parts[1])  # → datetime
    if len(parts) >= 3:
        m = re.search(r'(\d+)', parts[2])
        if m: doc["applicant_count"] = int(m.group(1))

    doc.pop("location", None)     # optional: drop raw field
    doc.pop("posted_date", None)  # we now have posted_at

    # ---------- seniority level ----------
    jd = doc["job_description"].lower()
    if re.search(r'\b(senior|sr\.)\b', jd):
        doc["seniority_level"] = "senior"
    elif re.search(r'\bmid[- ]?level\b', jd):
        doc["seniority_level"] = "mid"
    elif re.search(r'\bjunior|\bentry[- ]?level', jd):
        doc["seniority_level"] = "junior"

    # ---------- posting age ----------
    if "scraped_at" in doc and "posted_at" in doc:
        delta = doc["scraped_at"] - doc["posted_at"]
        doc["posting_age_days"] = delta.days

    return doc


CAN_PROVINCES = {
    "AB","BC","MB","NB","NL","NT","NS","NU","ON","PE","QC","SK","YT",
    "Alberta","British Columbia","Manitoba","New Brunswick","Newfoundland",
    "Nova Scotia","Ontario","Prince Edward Island","Quebec","Saskatchewan",
    "Yukon","Northwest Territories","Nunavut","Canada"
}
US_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA",
    "KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ",
    "NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT",
    "VA","WA","WV","WI","WY","United States","USA","US"
}

UK_REGIONS = {
    "UK","U.K.","United Kingdom","Great Britain","GB","GBR",
    "England","Scotland","Wales","Northern Ireland","NI"
}


CURRENCY_3LET = {"CAD","USD","GBP","EUR","AUD","NZD"}

def set_currency_code(doc: dict) -> None:
    if "currency_code" in doc:
        return

    salary_text = doc.get("job_description", "")

    # 1️⃣ explicit 3-letter code
    if m := re.search(r'\b(' + "|".join(CURRENCY_3LET) + r')\b', salary_text):
        doc["currency_code"] = m.group(1)
        return

    # 2️⃣ symbol-based inference
    symbol = doc.get("currency")
    location_blob = " ".join(
        str(x or "") for x in (
            doc.get("location"), doc.get("city"), doc.get("province")
        )
    )

    tokens = {t.strip(" ,.") for t in re.split(r'[·,\s]+', location_blob)}

    if symbol == "$":
        if tokens & CAN_PROVINCES:
            doc["currency_code"] = "CAD"
        elif tokens & US_STATES:
            doc["currency_code"] = "USD"
    elif symbol == "£":
        # direct map for pound sign
        doc["currency_code"] = "GBP"

    # 3️⃣ fallback: UK wording or postcode, even if symbol missing
    if "currency_code" not in doc:
        if tokens & UK_REGIONS:
            doc["currency_code"] = "GBP"
