import smtplib
import json
import random
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Settings ─────────────────────────────────────────────────────────────────
JSON_FILE   = "stoic_quotes.json"
NUM_QUOTES  = 1
DECAY_WEEKS = 4
SMTP_HOST   = "smtp.gmail.com"
SMTP_PORT   = 587

EMAIL_ADDRESS  = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# ── RSS feeds ─────────────────────────────────────────────────────────────────
FINANCE_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/companyNews",
    "https://www.ft.com/?format=rss",
]

TECH_FEEDS = [
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://feeds.feedburner.com/TechCrunch",
    "https://www.theverge.com/rss/index.xml",
]

# ── Essays (rotated daily) ────────────────────────────────────────────────────
ESSAYS = [
    ("The Tail End",                          "https://waitbutwhy.com/2015/12/the-tail-end.html"),
    ("Do Things That Don't Scale",            "https://paulgraham.com/ds.html"),
    ("Solitude and Leadership",               "https://theamericanscholar.org/solitude-and-leadership/"),
    ("The Feynman Technique",                 "https://fs.blog/feynman-technique/"),
    ("Diffusion of Responsibility",           "https://fs.blog/diffusion-of-responsibility/"),
    ("How to Think for Yourself",             "https://paulgraham.com/think.html"),
    ("The Cook and the Chef",                 "https://waitbutwhy.com/2015/11/the-cook-and-the-chef-musks-secret-sauce.html"),
    ("The Danger of a Single Story",          "https://fs.blog/the-danger-of-a-single-story/"),
    ("First Principles Thinking",             "https://fs.blog/first-principles/"),
    ("You and Your Research",                 "https://www.cs.virginia.edu/~robins/YouAndYourResearch.html"),
    ("The Age of Surveillance Capitalism",    "https://aeon.co/essays/we-are-the-product-of-our-data-but-we-are-not-just-data"),
    ("Keeping a Notebook",                    "https://www.brainpickings.org/2015/01/26/joan-didion-on-keeping-a-notebook/"),
    ("What I Wish I Knew When I Was 20",      "https://paulgraham.com/love.html"),
    ("The Paradox of Choice",                 "https://fs.blog/paradox-of-choice/"),
    ("On Saying No",                          "https://paulgraham.com/hwh.html"),
    ("The Map Is Not the Territory",          "https://fs.blog/map-and-territory/"),
    ("Why Procrastinators Procrastinate",     "https://waitbutwhy.com/2013/10/why-procrastinators-procrastinate.html"),
    ("The Courage to Be Disliked",            "https://aeon.co/essays/why-adler-was-right-about-the-courage-to-be-disliked"),
    ("Leverage Points",                       "https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/"),
    ("How to Be Successful",                  "https://blog.samaltman.com/how-to-be-successful"),
    ("The Anatomy of Determination",          "https://paulgraham.com/determination.html"),
    ("Compounding Knowledge",                 "https://fs.blog/compounding-knowledge/"),
    ("Making vs Managing",                    "https://paulgraham.com/makersschedule.html"),
    ("On Living Deliberately",               "https://aeon.co/essays/why-seneca-is-the-great-philosopher-of-time-and-how-to-use-it"),
    ("The Illusion of Explanatory Depth",     "https://fs.blog/illusion-of-explanatory-depth/"),
    ("Status Games",                          "https://aeon.co/essays/status-and-prestige-can-help-us-understand-human-behaviour"),
    ("Thinking in Systems",                   "https://fs.blog/thinking-in-systems/"),
    ("The Last Question",                     "https://web.archive.org/web/20130102043437/http://multivax.com/last_question.html"),
]

# ── Weight logic ──────────────────────────────────────────────────────────────
def current_weight(q):
    last = q.get("last_sent")
    if not last:
        return 1.0
    weeks = (date.today() - datetime.fromisoformat(last).date()).days // 7
    return min(1.0, weeks / DECAY_WEEKS)

# ── Load quotes ───────────────────────────────────────────────────────────────
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        quotes = json.load(f)
except FileNotFoundError:
    raise SystemExit(f"Error: {JSON_FILE} not found.")

for q in quotes:
    q.setdefault("weight", 1.0)
    q.setdefault("last_sent", None)

weights = [current_weight(q) for q in quotes]
chosen_quotes = random.choices(quotes, weights=weights, k=NUM_QUOTES)

# ── Fetch RSS news ────────────────────────────────────────────────────────────
def fetch_rss(feeds, n=3):
    items = []
    for url in feeds:
        if len(items) >= n:
            break
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                root = ET.fromstring(r.read())
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            # RSS 2.0
            for entry in root.iter("item"):
                title = (entry.findtext("title") or "").strip()
                link  = (entry.findtext("link")  or "").strip()
                if title and link:
                    items.append((title, link))
                if len(items) >= n:
                    break
            # Atom
            if len(items) < n:
                for entry in root.findall(".//atom:entry", ns):
                    title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
                    link_el = entry.find("atom:link", ns)
                    link = (link_el.get("href", "") if link_el is not None else "").strip()
                    if title and link:
                        items.append((title, link))
                    if len(items) >= n:
                        break
        except Exception:
            continue
    return items[:n]

finance_news = fetch_rss(FINANCE_FEEDS, 3)
tech_news    = fetch_rss(TECH_FEEDS,    3)

# ── Pick today's essay ────────────────────────────────────────────────────────
essay_title, essay_url = ESSAYS[date.today().toordinal() % len(ESSAYS)]

# ── Build HTML email ──────────────────────────────────────────────────────────
def news_rows(items, fallback_label):
    if not items:
        return f"<tr><td style='padding:6px 0;color:#888;'>Could not fetch {fallback_label} news.</td></tr>"
    rows = ""
    for title, link in items:
        rows += (
            f"<tr><td style='padding:5px 0;'>"
            f"<a href='{link}' style='color:#1a73e8;text-decoration:none;'>{title}</a>"
            f"</td></tr>"
        )
    return rows

html_body = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Georgia,serif;max-width:620px;margin:0 auto;padding:24px;color:#222;">

  <!-- Quote -->
  <h2 style="font-size:16px;font-weight:normal;color:#555;margin-bottom:24px;">
    Today's thought
  </h2>
  {"".join(f'<blockquote style="border-left:3px solid #ccc;margin:0 0 16px 0;padding:8px 16px;font-style:italic;color:#333;">{q["quote"]}</blockquote>' for q in chosen_quotes)}

  <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">

  <!-- Finance -->
  <h3 style="font-size:14px;letter-spacing:.05em;text-transform:uppercase;color:#888;margin:0 0 10px 0;">
    Finance
  </h3>
  <table style="width:100%;border-collapse:collapse;">
    {news_rows(finance_news, "finance")}
  </table>

  <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">

  <!-- Tech -->
  <h3 style="font-size:14px;letter-spacing:.05em;text-transform:uppercase;color:#888;margin:0 0 10px 0;">
    Technology
  </h3>
  <table style="width:100%;border-collapse:collapse;">
    {news_rows(tech_news, "tech")}
  </table>

  <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">

  <!-- Essay -->
  <p style="margin:0;font-size:13px;color:#888;">
    Today's essay &nbsp;→&nbsp;
    <a href="{essay_url}" style="color:#1a73e8;text-decoration:none;">{essay_title}</a>
  </p>

</body>
</html>
"""

# ── Send email ────────────────────────────────────────────────────────────────
def send_email():
    if not (EMAIL_ADDRESS and EMAIL_PASSWORD and EMAIL_RECEIVER):
        raise SystemExit("Error: Missing e-mail credentials in environment.")

    msg = MIMEMultipart("alternative")
    msg["From"]    = EMAIL_ADDRESS
    msg["To"]      = EMAIL_RECEIVER
    msg["Subject"] = "Today's thought"
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print("SMTP error:", e)

# ── Update weights & save ─────────────────────────────────────────────────────
def mark_as_sent():
    today_str = date.today().isoformat()
    for q in chosen_quotes:
        q["weight"]    = 0.0
        q["last_sent"] = today_str
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=2)

# ── Execute ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    send_email()
    mark_as_sent()
