"""Bronze layer: today's snapshot of current FDA drug labels, as received."""
import json
from datetime import date
from pathlib import Path

import requests

API = "https://api.fda.gov/drug/label.json"
DRUGS = ["metformin", "lisinopril", "atorvastatin", "amlodipine", "levothyroxine",
         "omeprazole", "albuterol", "sertraline", "warfarin", "ibuprofen"]


def fetch(drug, limit=10):
    """Current labels for one generic name. openFDA returns one record per label."""
    response = requests.get(API, params={"search": f'openfda.generic_name:"{drug}"', "limit": limit},
                            timeout=30)
    response.raise_for_status()
    return response.json()["results"]


def run(bronze_dir, day=None):
    """One file per day. Re-running on the same day overwrites it, so a retry is safe."""
    day = day or date.today().isoformat()
    records = [record for drug in DRUGS for record in fetch(drug)]
    bronze_dir = Path(bronze_dir)
    bronze_dir.mkdir(parents=True, exist_ok=True)
    path = bronze_dir / f"{day}.json"
    path.write_text(json.dumps(records))
    return path
