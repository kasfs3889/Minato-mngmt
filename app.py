import os
import sqlite3
import hmac
from datetime import datetime
from flask import Flask, request, Response, redirect, url_for, render_template_string, abort
from telegram_client import start_telegram, set_auto_reply, get_auto_reply, approve_draft, get_status

app = Flask(__name__)
DB_PATH = os.getenv("DB_PATH", "manager.db")
DASHBOARD_USER = os.getenv("DASHBOARD_USER", "admin")
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "")

HTML = """
<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Telegram Personal Manager</title>
<style>
body{font-family:system-ui;background:#101827;color:#e8eef8;max-width:900px;margin:28px auto;padding:0 14px}
.card{background:#1b2940;padding:18px;border-radius:14px;margin:14px 0}
button{padding:10px 15px;border:0;border-radius:8px;background:#2b83f6;color:white;font-weight:600}
small,.muted{color:#a9b8ce}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#111c2c;padding:12px;border-radius:8px}
.tag{padding:4px 8px;border-radius:7px;background:#31435f}
</style></head><body>
<h2>Telegram Personal Manager</h2>
<p class="muted">Private DM assistant · Gemini drafts · approval-first</p>
<div class="card">
 <p>Telegram: <b>{{ status }}</b></p>
 <p>Auto-reply: <span class="tag">{{ 'ON' if auto else 'OFF' }}</span></p>
 <form method="post" action="/toggle"><button>{{ 'Turn auto-reply OFF' if auto else 'Turn auto-reply ON' }}</button></form>
 <p class="muted">Auto-reply ON sends AI replies to eligible incoming private DMs. Keep OFF to review drafts first.</p>
</div>
<h3>Pending reply drafts</h3>
{% if drafts %}{% for d in drafts %}<div class="card">
 <b>Chat ID {{ d[1] }}</b> <small>{{ d[3] }}</small>
 <p><b>Incoming:</b></p><pre>{{ d[2] }}</pre>
 <p><b>AI draft:</b></p><pre>{{ d[4] }}</pre>
 <form method="post" action="/approve/{{ d[0] }}"><button>Approve & send</button></form>
</div>{% endfor %}{% else %}<p class="muted">No pending drafts.</p>{% endif %}
</body></html>
"""

def authorized():
    auth = request.authorization
    if not auth or auth.username != DASHBOARD_USER or not hmac.compare_digest(
        auth.password or "", DASHBOARD_PASSWORD
    ):
        return False
    return True

@app.before_request
def protect_dashboard():
    if request.path == "/health":
        return None
    if not DASHBOARD_PASSWORD:
        return Response("Set DASHBOARD_PASSWORD in environment before using dashboard.", 503)
    if not authorized():
        return Response("Login required", 401, {"WWW-Authenticate": 'Basic realm="Telegram Manager"'})

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/")
def home():
    with db() as conn:
        drafts = conn.execute(
            "SELECT id, chat_id, incoming_text, created_at, reply_text FROM drafts "
            "WHERE status='pending' ORDER BY id DESC LIMIT 30"
        ).fetchall()
    return render_template_string(HTML, drafts=drafts, auto=get_auto_reply(),
                                 status=get_status())

@app.post("/toggle")
def toggle():
    set_auto_reply(not get_auto_reply())
    return redirect(url_for("home"))

@app.post("/approve/<int:draft_id>")
def approve(draft_id):
    approve_draft(draft_id)
    return redirect(url_for("home"))

@app.get("/health")
def health():
    return {"ok": True, "service": "telegram-personal-manager", "time": datetime.utcnow().isoformat()}

start_telegram()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "10000")))
