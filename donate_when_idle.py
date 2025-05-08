import os, sys, time, json
from sqlalchemy import create_engine, text
import requests
# Configuration: default 'slack' domains (user can edit)
SLACK_DOMAINS = ["facebook", "twitter", "youtube", "netflix",
                 "reddit", "instagram", "tiktok", "amazon"]
# Required environment variables
goal = os.getenv("BEEMINDER_GOAL"); token = os.getenv("BEEMINDER_TOKEN")
if not goal or not token:
    sys.exit("Error: BEEMINDER_GOAL and BEEMINDER_TOKEN must be set")
# Optional environment variables (with defaults)
openai_key = os.getenv("OPENAI_KEY")
cloud_mode = os.getenv("CLOUD_MODE", "0") not in ("0", "false", None)
idle_min = int(os.getenv("IDLE_MINUTES", "5"))
dev_share = float(os.getenv("DEV_SHARE", "0.10"))
# Determine ActivityWatch SQLite database path
if sys.platform.startswith("win"):
    db_path = os.path.expandvars(
        "%LOCALAPPDATA%/activitywatch/activitywatch/aw-server/peewee-sqlite.v2.db")
elif sys.platform == "darwin":
    db_path = os.path.expanduser(
        "~/Library/Application Support/activitywatch/aw-server/peewee-sqlite.v2.db")
else:
    db_path = os.path.expanduser(
        "~/.local/share/activitywatch/aw-server/peewee-sqlite.v2.db")
db_path = db_path.replace("\\", "/")
engine = create_engine(f"sqlite:///{db_path}")
# Beeminder and OpenAI API setup
beeminder_url = f"https://beeminder.com/api/v1/users/me/goals/{goal}/datapoints.json"
openai_url = "https://api.openai.com/v1/chat/completions" if openai_key and cloud_mode else None
openai_headers = {"Authorization": f"Bearer {openai_key}",
                  "Content-Type": "application/json"} if openai_url else {}
print(f"Monitoring idle time (threshold {idle_min} min) and slack activity...")
try:
    while True:
        # Query latest ActivityWatch events for AFK and active window
        with engine.connect() as conn:
            afk = conn.execute(text(
                "SELECT timestamp, duration, data FROM event JOIN bucket "
                "ON event.bucket_id = bucket.id "
                "WHERE bucket.id LIKE 'aw-watcher-afk%' "
                "ORDER BY event.timestamp DESC LIMIT 1"
            )).one_or_none()
            win = conn.execute(text(
                "SELECT data FROM event JOIN bucket "
                "ON event.bucket_id = bucket.id "
                "WHERE bucket.id LIKE 'aw-watcher-window%' "
                "ORDER BY event.timestamp DESC LIMIT 1"
            )).one_or_none()
        idle_trigger = False; slack_trigger = False
        if afk and afk[2] and json.loads(afk[2]).get("status") == "afk" \
                and float(afk[1]) / 60.0 >= idle_min:
            idle_trigger = True
        if not idle_trigger and win:
            win_data = json.loads(win[0])
            app = win_data.get("app", ""); title = win_data.get("title", "")
            if openai_url:
                prompt = f"The user is using {app} with window title '{title}'."
                prompt += " Is this activity productive work or slacking off?"
                body = {"model": "gpt-3.5-turbo",
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": 1, "temperature": 0}
                try:
                    res = requests.post(openai_url, headers=openai_headers,
                                        json=body, timeout=10)
                    if res.status_code == 200:
                        ans = res.json()['choices'][0]['message']['content']
                        slack_trigger = ans.strip().lower().startswith("slack")
                except Exception:
                    slack_trigger = False
            else:
                text_data = (app + " " + title).lower()
                if any(d in text_data for d in SLACK_DOMAINS):
                    slack_trigger = True
        if idle_trigger or slack_trigger:
            reason = "idle" if idle_trigger else "slack"
            print(f"Triggering donation (reason: {reason})")
            requests.post(beeminder_url,
                          params={"auth_token": token},
                          json={"value": 1,
                                "comment": f"auto-donation due to {reason}"},
                          timeout=5)
            try:
                requests.post("http://localhost:8000/ledger",
                              json={"charity_share": round(1.0 - dev_share, 2),
                                    "dev_share": dev_share},
                              timeout=3)
            except Exception:
                pass
        time.sleep(60)
except KeyboardInterrupt:
    print("Stopping monitoring.")
