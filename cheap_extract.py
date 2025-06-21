import re
from flashtext import KeywordProcessor
from datetime import datetime
from textwrap import shorten

# -------------- keyword inventories -----------------
EMPLOY_TYPES   = {"full[- ]?time":"full-time",
                  "part[- ]?time":"part-time",
                  "contract":"contract",
                  "intern":"internship",
                  "temporary":"temporary"}
WORKPLACE_TYPES= {"remote":"remote",
                  "hybrid":"hybrid",
                  "on[- ]?site":"on-site"}
DEGREE_KEYWORDS= {"phd":"PhD",
                  "doctor":"PhD",
                  "master":"Master",
                  "msc":"Master",
                  "bachelor":"Bachelor",
                  "ba ":"Bachelor",
                  "bs ":"Bachelor",
                  "bsc":"Bachelor"}
BENEFITS_LIST  = ["401(k)","RRSP","health benefits",
                  "dental","vision","parental leave",
                  "equity","RSU","stock options",
                  "wellness","flexible vacation",
                  "remote stipend","learning budget"]

SKILLS = {"python","sql","excel","bigquery","data analytics",
          "economic research","presentation","scikit-learn",
          "pandas","spark"}   

kp_benefits = KeywordProcessor(case_sensitive=False)
for b in BENEFITS_LIST: kp_benefits.add_keyword(b)

kp_skills = KeywordProcessor(case_sensitive=False)
for s in SKILLS: kp_skills.add_keyword(s)

# main extractor ---------------------------------------------------------------
def cheap_extract(text: str) -> dict:
    out = {}

    # ---------- employment / workplace type ----------
    for pat, val in EMPLOY_TYPES.items():
        if re.search(rf'\b{pat}\b', text, re.I):
            out["employment_type"] = val
            break

    for pat, val in WORKPLACE_TYPES.items():
        if re.search(rf'\b{pat}\b', text, re.I):
            out["workplace_type"] = val
            break

    # ---------- degree requirements ----------
    for pat, level in DEGREE_KEYWORDS.items():
        if re.search(rf'\b{pat}', text, re.I):
            out["degree_required"] = level
            break

    # ---------- benefits ----------
    benefits_found = kp_benefits.extract_keywords(text)
    if benefits_found:
        out["benefits"] = sorted({b.lower() for b in benefits_found})


    # ---------- skills ----------
    # out["required_skills"] = sorted(set(kp_skills.extract_keywords(text)))

    # ---------- clean description (no excess whitespace) ----------
    clean = re.sub(r'\s+', ' ', text).strip()
    # (optional) store a truncated preview for quick display
    out["description_clean"] = shorten(clean, width=300, placeholder="…")

    return out