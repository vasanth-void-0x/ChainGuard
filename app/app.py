"""
ChainGuard Demo App -- Intentionally Vulnerable Flask API
-----------------------------------------------------------
WARNING: This app contains deliberate security flaws for the sole
purpose of demonstrating ChainGuard's automated security scanning
pipeline (Gitleaks, Semgrep, Trivy). DO NOT deploy this code anywhere.

Vulnerabilities included (on purpose):
1. Hardcoded API key / secret            -> caught by Gitleaks
2. SQL Injection (string formatting)     -> caught by Semgrep
3. Use of eval() on user input           -> caught by Semgrep
4. Debug mode enabled in "production"    -> caught by Semgrep
5. Outdated/vulnerable dependencies      -> caught by Trivy (see requirements.txt)
"""

import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- VULNERABILITY 1: Hardcoded secret (Gitleaks should flag this) ---
GROQ_API_KEY = "gsk_live_51J8x9FakeDemoKeyDoNotUse1234567890abcdefEXAMPLE"
DB_PASSWORD = "SuperSecretPassword123!"


def get_db_connection():
    conn = sqlite3.connect("demo.db")
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def home():
    return jsonify({"service": "ChainGuard Demo API", "status": "running"})


@app.route("/login", methods=["POST"])
def login():
    """--- VULNERABILITY 2: SQL Injection via string formatting ---"""
    username = request.form.get("username", "")
    password = request.form.get("password", "")

    conn = get_db_connection()
    # Unsafe: user input directly formatted into SQL query
    query = "SELECT * FROM users WHERE username = '%s' AND password = '%s'" % (
        username,
        password,
    )
    cursor = conn.execute(query)
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({"status": "success", "message": "Logged in"})
    return jsonify({"status": "failed", "message": "Invalid credentials"}), 401


@app.route("/calculate", methods=["POST"])
def calculate():
    """--- VULNERABILITY 3: eval() on user-supplied input ---"""
    expression = request.json.get("expression", "0")
    result = eval(expression)  # noqa: unsafe by design, for scanner demo
    return jsonify({"result": result})


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    # --- VULNERABILITY 4: debug=True should never run in production ---
    app.run(host="0.0.0.0", port=5000, debug=True)
