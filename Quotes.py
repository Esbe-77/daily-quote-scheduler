import smtplib
import json
import random
import os
from datetime import date, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ──------ Settings ──────────────────────────────────────────────────────────
JSON_FILE = "stoic_quotes.json"          # your weighted-quotes file
NUM_QUOTES = 1                              # how many quotes per e-mail
DECAY_WEEKS = 4                             # zero → full weight after N weeks
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

# e-mail credentials from env
EMAIL_ADDRESS  = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# ──----- Weight logic ──────────────────────────────────────────────────────
def current_weight(q):
    """
    Return the draw-weight for a quote.
    • First use ⇒ 1 .0
    • After being sent, weight ramps linearly 0 → 1 over DECAY_WEEKS.
    """
    last = q.get("last_sent")
    if not last:
        return 1.0
    weeks = (date.today() - datetime.fromisoformat(last).date()).days // 7
    return min(1.0, weeks / DECAY_WEEKS)

# ──----- Load quotes ────────────────────────────────────────────────────────
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        quotes = json.load(f)
except FileNotFoundError:
    raise SystemExit(f"Error: {JSON_FILE} not found.")

# Gracefully handle legacy entries without the new fields
for q in quotes:
    q.setdefault("weight", 1.0)
    q.setdefault("last_sent", None)

weights = [current_weight(q) for q in quotes]
chosen_quotes = random.choices(quotes, weights=weights, k=NUM_QUOTES)

# ──----- Compose e-mail ─────────────────────────────────────────────────────
subject = "Today’s thought"
body = "\n\n".join(f"- {q['quote']}" for q in chosen_quotes)

def send_email():
    if not (EMAIL_ADDRESS and EMAIL_PASSWORD and EMAIL_RECEIVER):
        raise SystemExit("Error: Missing e-mail credentials in environment.")

    msg = MIMEMultipart()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print("SMTP error:", e)

# ──----- Update weights & save file ────────────────────────────────────────
def mark_as_sent():
    today_str = date.today().isoformat()
    for q in chosen_quotes:
        q["weight"] = 0.0
        q["last_sent"] = today_str
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=2)

# ──----- Execute ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    send_email()
    mark_as_sent()
