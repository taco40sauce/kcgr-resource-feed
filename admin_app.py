import os
import json
import time
import base64
import subprocess
from pathlib import Path
from functools import wraps
import requests
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

# --- Records/removal panel config ---------------------------------------
GITHUB_REPO = os.environ.get("GITHUB_REPO", "taco40sauce/kcgr-resource-feed")
GITHUB_PAT = os.environ.get("GITHUB_PAT")  # repo-scoped: Contents read-only, Actions read/write
LOCAL_RECORDS_PATH = Path(
    os.environ.get("KCGR_LOCAL_RECORDS_PATH", str(Path.home() / "kcgr-pipeline" / "data" / "records.json"))
)  # confirmed 8/14/2026: /home/dave/kcgr-pipeline/data/records.json

# Each source: which file it lives in, how to read it, which removal workflow (if any) handles it
SOURCES = {
    "pi-aprs": {
        "label": "Pi APRS", "kind": "local", "path": LOCAL_RECORDS_PATH,
        "removal_workflow": None,  # no removal tool exists for this source yet
    },
    "aprs-is": {
        "label": "APRS-IS", "kind": "github", "path": "backups/records_backup_aprsis.json",
        "removal_workflow": "aprsis-removal.yml",
    },
    "winlink": {
        "label": "Winlink", "kind": "github", "path": "winlink/records.json",
        "removal_workflow": "winlink-removal.yml",
    },
}


def gh_headers():
    return {
        "Authorization": f"Bearer {GITHUB_PAT}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def gh_get_json_file(path):
    """Read a JSON file from the repo via the Contents API (avoids raw.githubusercontent.com's cache lag)."""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{path}"
    r = requests.get(url, headers=gh_headers(), timeout=10)
    r.raise_for_status()
    content = base64.b64decode(r.json()["content"]).decode("utf-8")
    return json.loads(content) if content.strip() else {}


def read_local_json(path):
    if not path.exists():
        return {}
    text = path.read_text().strip()
    return json.loads(text) if text else {}


def gh_dispatch_workflow(workflow_file, inputs=None):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{workflow_file}/dispatches"
    body = {"ref": "main"}
    if inputs:
        body["inputs"] = inputs
    r = requests.post(url, headers=gh_headers(), json=body, timeout=10)
    r.raise_for_status()


def gh_latest_run_status(workflow_file):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/{workflow_file}/runs"
    r = requests.get(url, headers=gh_headers(), params={"per_page": 1}, timeout=10)
    r.raise_for_status()
    runs = r.json().get("workflow_runs", [])
    return runs[0] if runs else None
# --------------------------------------------------------------------------


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
  {% if error %}<p style="color: red;">{{ error }}</p>{% endif %}
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
     <a href="{{ url_for('records') }}">View/remove active records</a> &nbsp;|&nbsp;
     <a href="{{ url_for('logout') }}">Log out</a></p>
</body>
"""

RECORDS_PAGE = """
<!doctype html>
<title>KCGR Admin — Records</title>
<body style="font-family: sans-serif; max-width: 900px; margin: 40px auto;">
  <h2>Active Records — All Sources</h2>
  {% if error %}<p style="color: red;">{{ error }}</p>{% endif %}
  <table border="1" cellpadding="8" style="border-collapse: collapse; width: 100%;">
    <tr><th>Source</th><th>Identity</th><th>Category</th><th>Status</th><th>Location</th><th>Callsign</th><th></th></tr>
    {% for r in records %}
    <tr>
      <td>{{ r.source_label }}</td>
      <td style="font-family: monospace;">{{ r.identity }}</td>
      <td>{{ r.category_mapped }}</td>
      <td>{{ r.status_mapped }}</td>
      <td>{{ r.location }}</td>
      <td>{{ r.callsign }}</td>
      <td>
        {% if r.removal_workflow %}
          <a href="{{ url_for('records_confirm', source=r.source_key, identity=r.identity) }}">Remove</a>
        {% else %}
          <span style="color: #999;">no removal tool</span>
        {% endif %}
      </td>
    </tr>
    {% endfor %}
    {% if not records %}
    <tr><td colspan="7" style="text-align: center; color: #666;">No active records on any source.</td></tr>
    {% endif %}
  </table>
  <p><a href="{{ url_for('index') }}">&larr; Back</a></p>
</body>
"""

CONFIRM_PAGE = """
<!doctype html>
<title>Confirm removal</title>
<body style="font-family: sans-serif; max-width: 500px; margin: 80px auto;">
  <h2>Remove this record?</h2>
  <p><strong>Source:</strong> {{ source_label }}<br>
     <strong>Identity:</strong> <code>{{ identity }}</code></p>
  <form method="post" action="{{ url_for('records_remove') }}">
    <input type="hidden" name="source" value="{{ source_key }}">
    <input type="hidden" name="identity" value="{{ identity }}">
    <button type="submit" style="font-size: 1.1em; padding: 10px 24px; background: #dc2626; color: white; border: none; border-radius: 6px;">
      Yes, remove it
    </button>
  </form>
  <p><a href="{{ url_for('records') }}">Cancel</a></p>
</body>
"""

RESULT_PAGE = """
<!doctype html>
<title>Removal result</title>
<body style="font-family: sans-serif; max-width: 600px; margin: 80px auto;">
  <h2>{{ 'Done' if ok else 'Something went wrong' }}</h2>
  <p>{{ message }}</p>
  <p><a href="{{ url_for('records') }}">&larr; Back to records</a></p>
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
    error = session.pop("toggle_error", None)
    return render_template_string(ADMIN_PAGE, status=status, poll_interval=poll_interval, error=error)
@app.route("/refresh")
@login_required
def refresh():
    return redirect(url_for("index"))
@app.route("/toggle", methods=["POST"])
@login_required
def toggle():
    action = request.form.get("action")
    if action in ("start", "stop"):
        result = subprocess.run(["sudo", "systemctl", action, SERVICE_NAME], timeout=10)
        if result.returncode != 0:
            session["toggle_error"] = f"Command failed (exit {result.returncode}) — check sudoers config on the Pi."
    return redirect(url_for("index"))


@app.route("/records")
@login_required
def records():
    error = None
    all_records = []
    for key, cfg in SOURCES.items():
        try:
            data = read_local_json(cfg["path"]) if cfg["kind"] == "local" else gh_get_json_file(cfg["path"])
        except Exception as e:
            error = f"Couldn't read {cfg['label']}: {e}"
            data = {}
        for identity, rec in data.items():
            all_records.append({
                "source_key": key,
                "source_label": cfg["label"],
                "removal_workflow": cfg["removal_workflow"],
                "identity": identity,
                "category_mapped": rec.get("category_mapped", "--"),
                "status_mapped": rec.get("status_mapped", "--"),
                "location": rec.get("location", "--"),
                "callsign": rec.get("callsign", "--"),
            })
    return render_template_string(RECORDS_PAGE, records=all_records, error=error)


@app.route("/records/confirm")
@login_required
def records_confirm():
    source = request.args.get("source")
    identity = request.args.get("identity")
    cfg = SOURCES.get(source)
    if not cfg or not cfg["removal_workflow"]:
        return redirect(url_for("records"))
    return render_template_string(CONFIRM_PAGE, source_key=source, identity=identity, source_label=cfg["label"])


@app.route("/records/remove", methods=["POST"])
@login_required
def records_remove():
    source = request.form.get("source")
    identity = request.form.get("identity")
    cfg = SOURCES.get(source)
    if not cfg or not cfg["removal_workflow"]:
        return render_template_string(RESULT_PAGE, ok=False, message="Unknown or non-removable source.")

    try:
        gh_dispatch_workflow(cfg["removal_workflow"], inputs={"action": "remove", "identity": identity})
    except Exception as e:
        return render_template_string(RESULT_PAGE, ok=False, message=f"Failed to trigger removal: {e}")

    # Poll for the removal run to actually finish before publishing —
    # don't just fire-and-hope like the workflow_run trigger already has once today.
    removal_run = None
    for _ in range(20):  # ~40s max
        time.sleep(2)
        run = gh_latest_run_status(cfg["removal_workflow"])
        if run and run.get("status") == "completed":
            removal_run = run
            break

    if not removal_run:
        return render_template_string(RESULT_PAGE, ok=False,
            message="Removal was triggered but didn't finish within the wait window — check GitHub Actions directly.")
    if removal_run.get("conclusion") != "success":
        return render_template_string(RESULT_PAGE, ok=False,
            message=f"Removal run finished with conclusion '{removal_run.get('conclusion')}' — check its log before assuming anything changed.")

    try:
        gh_dispatch_workflow("merge-and-publish.yml")
    except Exception as e:
        return render_template_string(RESULT_PAGE, ok=False,
            message=f"Removal succeeded but triggering the map republish failed: {e}. Run merge-and-publish manually.")

    return render_template_string(RESULT_PAGE, ok=True,
        message=f"Removed {identity} from {cfg['label']} and triggered a map republish. Give it a minute, then check the map.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
