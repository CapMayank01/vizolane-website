import os
import sys
import time

# Ensure parent directory is in sys.path so 'api' package can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

# Load environment variables
load_dotenv(override=True)

# Resolve templates and static folders relative to the root directory
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)

app = Flask(
    __name__,
    template_folder=os.path.join(root_dir, "templates"),
    static_folder=os.path.join(root_dir, "static")
)

# Enable CORS
allowed_origins = [
    url.strip() for url in os.getenv("FRONTEND_URL", "http://localhost:5500").split(",")
]
allowed_origins.extend([
    "http://localhost:8001", "http://127.0.0.1:8001",
    "http://localhost:8000", "http://127.0.0.1:8000",
    "http://localhost:3000", "http://127.0.0.1:3000"
])
CORS(app, origins=allowed_origins)

# Import services
from api.services.email_service import (
    send_admin_notification,
    send_user_confirmation,
    verify_connection,
)
from api.services.sheets_service import init_sheets, append_contact_to_sheet
from api.services.github_db_service import write_to_github_db

# Initialize services on start
with ThreadPoolExecutor(max_workers=2) as executor:
    executor.submit(verify_connection)
    executor.submit(init_sheets)

# Simple in-memory rate limiting dictionary
# Store structure: { ip: [timestamp1, timestamp2, ...] }
ip_limit_store = {}
LIMIT_WINDOW = 15 * 60  # 15 minutes in seconds
LIMIT_MAX_REQUESTS = 5


def is_rate_limited(ip):
    now = time.time()
    if ip not in ip_limit_store:
        ip_limit_store[ip] = []

    # Clean old requests outside the window
    ip_limit_store[ip] = [t for t in ip_limit_store[ip] if now - t < LIMIT_WINDOW]

    if len(ip_limit_store[ip]) >= LIMIT_MAX_REQUESTS:
        return True

    ip_limit_store[ip].append(now)
    return False


# ── Page Routes ───────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/founder")
def founder():
    return render_template("founder.html")


@app.route("/update-portfolio")
def update_portfolio():
    return render_template("update_portfolio.html")


# ── Health Check ──────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })


# ── POST /api/contact ────────────────────────────────────

@app.route("/api/contact", methods=["POST"])
def contact():
    # Rate limiting check
    client_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    if is_rate_limited(client_ip):
        return jsonify({
            "success": False,
            "error": "Too many requests. Please try again after 15 minutes."
        }), 429

    try:
        # Support both JSON and Form URL-encoded data
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form.to_dict()

        name = data.get("name", "")
        email = data.get("email", "")
        phone = data.get("phone", "")
        message = data.get("message", "")

        # ── Validation ────────────────────────────────
        errors = []
        if not name or not isinstance(name, str) or len(name.strip()) < 2:
            errors.append("Name is required (at least 2 characters).")
        if not email or not isinstance(email, str) or "@" not in email:
            errors.append("A valid email address is required.")
        if not message or not isinstance(message, str) or len(message.strip()) < 5:
            errors.append("Message is required (at least 5 characters).")

        if errors:
            return jsonify({"success": False, "errors": errors}), 400

        # Sanitize
        contact_data = {
            "name": name.strip(),
            "email": email.strip().lower(),
            "phone": phone.strip() if phone else "",
            "message": message.strip(),
        }

        print(f"\n[NEW MAIL] New contact from: {contact_data['name']} <{contact_data['email']}>")

        # Execute operations concurrently using thread pool
        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_sheets = executor.submit(append_contact_to_sheet, contact_data)
            future_github = executor.submit(write_to_github_db, contact_data)
            future_admin = executor.submit(send_admin_notification, contact_data)
            future_user = executor.submit(send_user_confirmation, contact_data)

            # Wait for all to complete and check status
            try:
                future_sheets.result()
                results.append(("Google Sheets", True))
            except Exception as e:
                print(f"[ERROR] Google Sheets failed: {e}")
                results.append(("Google Sheets", False))

            try:
                git_res = future_github.result()
                results.append(("GitHub DB", git_res))
            except Exception as e:
                print(f"[ERROR] GitHub DB failed: {e}")
                results.append(("GitHub DB", False))

            try:
                future_admin.result()
                results.append(("Admin Email", True))
            except Exception as e:
                print(f"[ERROR] Admin Email failed: {e}")
                results.append(("Admin Email", False))

            try:
                future_user.result()
                results.append(("User Email", True))
            except Exception as e:
                print(f"[ERROR] User Email failed: {e}")
                results.append(("User Email", False))

        # Log results
        for label, success in results:
            status_text = "success" if success else "failed"
            print(f"   {label}: {status_text}")

        # Check if at least one critical operation succeeded
        sheets_success = results[0][1]
        github_success = results[1][1]
        admin_email_success = results[2][1]
        user_email_success = results[3][1]

        if not sheets_success and not github_success and not admin_email_success and not user_email_success:
            return jsonify({
                "success": False,
                "error": "Failed to process your submission. Please try again or email us directly at admin@vizolane.com."
            }), 500

        return jsonify({
            "success": True,
            "message": "Thank you! Your message has been received. We'll get back to you soon."
        })

    except Exception as err:
        print(f"[ERROR] Unexpected error in /api/contact: {err}")
        return jsonify({
            "success": False,
            "error": "Something went wrong. Please try again or email us at admin@vizolane.com."
        }), 500


# Start local server if run directly
if __name__ == "__main__":
    port = int(os.getenv("PORT", 3000))
    print(f"\n[START] Starting Vizolane Contact Backend...\n")
    app.run(host="0.0.0.0", port=port, debug=True)
