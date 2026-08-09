import os
import subprocess
from pathlib import Path
from functools import wraps

from dotenv import load_dotenv
from flask import Flask, request, redirect, url_for, session, render_template_string

load_dotenv(Path.home() / ".kcgr_secrets" / "credentials.env")

app = Flask(__name__)
app.secret_key = os.environ.get("ADMIN_APP_SECRET_KEY", os.urandom(24))

ADMIN_PASSWORD = os.environ.get("KCGR_ADMIN_PASSWORD")
SERVICE_NAME = "kcgr-pipeline"

if not ADMIN_PASSWORD:
    raise RuntimeError(
        "KCGR_ADMIN_PASSWORD is not set. Add it to ~/.kcgr_secrets/credentials.env "
        "before running this app."
    )


def login_required(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped


LOGIN_PAGE = """
<!doctype html>
<title>KCGR Admin — Login</title>
<body style="font-family: sans-serif; max-width: 400px; margin: 80px auto;">
  <h2>KCGR Pipeline Admin</h2>
  {% if error %}<p style="color: red;">{{ error }}</p>{% endif %}
  <form method="post">
    <input type="password" name="password" placeholder="Password" autofocus
           style="font-size: 1.1em; padding: 8px; width: 100%;">
    <br><br>
    <button type="submit" style="font-size: 1.1em; padding: 8px 20px;">Log in</button>
  </form>
</body>
"""

ADMIN_PAGE = """
<!doctype html>
<title>KCGR Admin</title>
<body style="font-family: sans-serif; max-width: 500px; margin: 60px auto;">
  <h2>KCGR Pipeline Admin</h2>
  <p><strong>Pipeline status:</strong>
    <span style="color: {{ 'green' if status == 'active' else 'gray' }};">{{ status }}</span>
  </p>
  <form method="post" action="{{ url_for('toggle') }}" style="margin-bottom: 30px;">
    {% if status == 'active' %}
      <button name="action" value="stop" type="submit"
              style="font-size: 1.2em; padding: 12px 30px; background: #dc2626; color: white; border: none; border-radius: 6px;">
        Turn OFF
      </button>
    {% else %}
      <button name="action" value="start" type="submit"
              style="font-size: 1.2em; padding: 12px 30px; background: #16a34a; color: white; border: none; border-radius: 6px;">
        Turn ON
      </button>
    {% endif %}
  </form>
  <p style="color: #666; font-size: 0.9em;">
    When ON, the pipeline polls every {{ poll_interval }} seconds for new KCGR reports
    and pushes updates to the public map automatically.
  </p>
  <p><a href="{{ url_for('refresh') }}">Refresh status</a> &nbsp;|&nbsp;
     <a href="{{ url_for('logout') }}">Log out</a></p>
</body>
"""


def get_service_status():
    try:
        result = subprocess.run(
            ["systemctl", "is-active", SERVICE_NAME],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("index"))
        error = "Incorrect password"
    return render_template_string(LOGIN_PAGE, error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    status = get_service_status()
    poll_interval = os.environ.get("POLL_INTERVAL_SECONDS", "900")
    return render_template_string(ADMIN_PAGE, status=status, poll_interval=poll_interval)


@app.route("/refresh")
@login_required
def refresh():
    return redirect(url_for("index"))


@app.route("/toggle", methods=["POST"])
@login_required
def toggle():
    action = request.form.get("action")
    if action in ("start", "stop"):
        subprocess.run(["sudo", "systemctl", action, SERVICE_NAME], timeout=10)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
