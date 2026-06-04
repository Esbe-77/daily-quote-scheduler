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

# ── Chess lessons (rotated daily) ────────────────────────────────────────────
CHESS_LESSONS = [
    ("Control the Centre",        "Your first priority in any game. Place pawns on e4/d4 (or e5/d5 as Black) and develop pieces toward the middle. A piece in the centre controls more squares than one on the edge."),
    ("Develop Every Piece",       "Get your knights and bishops off the back rank before you start attacking. A rule of thumb: don't move the same piece twice in the opening unless you have to. Every undeveloped piece is a wasted turn."),
    ("King Safety — Castle Early","After developing your minor pieces, castle. Your king is a liability in the centre during the middlegame. Castling tucks it away and connects your rooks."),
    ("The Fork",                  "A fork is a single piece attacking two enemy pieces at once, forcing your opponent to lose one. Knights are the best forkers — their L-shape lets them attack squares no other piece covers. Always scan for knight forks after exchanges."),
    ("The Pin",                   "A pin locks a piece in place because moving it would expose a more valuable piece behind it. Absolute pins (pinned to the king) are the strongest — the piece literally cannot move. Use pins to win material or restrict your opponent."),
    ("The Skewer",                "The reverse of a pin. You attack a high-value piece; when it moves, you win the lesser piece behind it. Rooks and bishops are the classic skewering pieces. Look for skewers along open files and diagonals."),
    ("Discovered Attack",         "Move one piece to unleash an attack from another behind it. The moving piece can also create its own threat, making it doubly dangerous. Discovered checks are especially powerful — your opponent must deal with the check first."),
    ("Rooks Belong on Open Files","A rook on a closed file does almost nothing. Put rooks on files with no pawns, or half-open files (no friendly pawn). Two rooks doubled on an open file is one of the most powerful structures in chess."),
    ("Trade Pieces When Ahead",   "If you're up material, simplify. Trade pieces to reduce your opponent's counterplay and make your advantage easier to convert. Avoid trades when you're behind — you need chaos and complications to come back."),
    ("The 1-2-3 of Pawn Endings", "In king-and-pawn endgames, three things win: (1) King activity — centralise your king immediately. (2) Passed pawns — a pawn with no opposing pawn blocking it or on adjacent files. (3) Opposition — the side whose king forces the other back. Learn these and you'll convert endgames others draw."),
    ("Don't Move Your Queen Early","A premature queen sortie gets punished. Your opponent develops with tempo by chasing it. Bring out knights and bishops first, secure your king, then activate the queen when it has safe, useful squares."),
    ("Think in Forcing Moves First","Before any move, scan for checks, captures, and threats — in that order. Forcing moves limit your opponent's options. Calculate those lines before quieter moves. Many games are decided by a tactic hiding in plain sight."),
    ("Pawn Structure is Permanent","Unlike pieces, pawns can't go backwards. Doubled pawns, isolated pawns, and backward pawns are long-term weaknesses. Before pushing a pawn, ask: what does this create? Weak squares and open files last the whole game."),
    ("The Outpost",               "A square that can't be attacked by an enemy pawn is an outpost. A knight planted on an outpost deep in enemy territory is often worth as much as a rook. Create outposts by trading or advancing pawns to clear the attacking pawn."),
    ("Rook + King Checkmate",     "The most common endgame to know. Use the ladder method: put your rook on the edge of the board, drive the enemy king to the edge rank by rank, then bring your king over to help deliver mate. Practice this until it's automatic."),
    ("Bishops vs Knights",        "Open positions favour bishops — they cover long diagonals and distant squares quickly. Closed positions with locked pawns favour knights — they can hop over pawns and reach squares bishops can't. Always consider which piece suits the structure."),
    ("The Zwischenzug",           "A 'between move' — instead of recapturing immediately, you play a forcing move first (usually a check or big threat). Your opponent must respond, and then you recapture, often with an improved result. Always ask: before I take back, is there something better?"),
    ("Piece Activity Over Material","A rook doing nothing is worth less than a bishop tearing up a diagonal. When evaluating a position, ask how active each piece is. Sometimes sacrificing a pawn to open lines and activate your pieces is objectively stronger than holding the material."),
    ("Triangulation",             "A king manoeuvre in endgames to lose a tempo and gain the opposition. If your king needs to reach a square but direct paths keep the opposition equal, triangulate — take three moves to do what one would, forcing your opponent into a losing structure."),
    ("The 50-Move Rule & Zugzwang","In endgames, two concepts matter: zugzwang (any move you make worsens your position — used to force a win) and the 50-move rule (50 moves without a capture or pawn move = draw). Knowing these prevents you from winning a won endgame incorrectly or letting a draw slip."),
]

# ── Pick today's essay & chess lesson ────────────────────────────────────────
essay_title, essay_url = ESSAYS[date.today().toordinal() % len(ESSAYS)]
chess_title, chess_body = CHESS_LESSONS[date.today().toordinal() % len(CHESS_LESSONS)]

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

  <!-- Chess -->
  <h3 style="font-size:14px;letter-spacing:.05em;text-transform:uppercase;color:#888;margin:0 0 10px 0;">
    Chess
  </h3>
  <p style="margin:0 0 6px 0;font-size:14px;font-weight:bold;color:#333;">{chess_title}</p>
  <p style="margin:0;font-size:14px;color:#444;line-height:1.6;">{chess_body}</p>

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
