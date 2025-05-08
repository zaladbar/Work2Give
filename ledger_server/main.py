from fastapi import FastAPI
from pathlib import Path
import json, datetime

app = FastAPI()
LEDGER_FILE = Path(__file__).parent / "ledger.json"
if not LEDGER_FILE.exists():
    LEDGER_FILE.write_text("[]")

@app.post("/ledger")
def add_ledger_entry(charity_share: float, dev_share: float):
    try:
        ledger = json.loads(LEDGER_FILE.read_text())
    except json.JSONDecodeError:
        ledger = []
    entry = {
        "charity_share": charity_share,
        "dev_share": dev_share,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
    ledger.append(entry)
    LEDGER_FILE.write_text(json.dumps(ledger))
    return entry

@app.get("/ledger/latest")
def get_latest_entry():
    try:
        ledger = json.loads(LEDGER_FILE.read_text())
    except FileNotFoundError:
        return {"error": "No ledger file"}
    if ledger:
        return ledger[-1]
    return {"error": "No entries"}
