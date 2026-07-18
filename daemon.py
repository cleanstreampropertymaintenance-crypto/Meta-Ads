import time
import json
import os
import smtplib
import sys
import threading
import urllib.request
import urllib.error
from datetime import datetime, timezone
from email.mime.text import MIMEText
from flask import Flask, request, jsonify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from meta_client import MetaAdsClient
from config import (
    TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, TWILIO_TO_NUMBER,
    NOTIFY_EMAIL, NOTIFY_EMAIL_PASSWORD
)
from twilio.rest import Client as TwilioClient

QUOTEIQ_ENDPOINT   = "https://us-central1-quoteiq-2.cloudfunctions.net/submitFormV2Public"
QUOTEIQ_USER_ID    = "rRDPZxRScANBnOIncc4Wyg0XhNa2"
QUOTEIQ_COMPANY_ID = "A8Jt6Sd6HhrqAhOTbzrV"
QUOTEIQ_FORM_ID    = "FJ2BOTkhlGM1s84GSKZU"
QUOTEIQ_CHANNEL_ID = "6MkxiLRNZF8nwHV5zxAB"

# QuoteIQ form field IDs (from /api/forms/v2/FJ2BOTkhlGM1s84GSKZU)
QIQ_FIRST_NAME  = "1779211674516000_0"
QIQ_LAST_NAME   = "1779211674516000_1"
QIQ_EMAIL       = "1779211674516000_2"
QIQ_PHONE       = "1779211674516000_3"
QIQ_ADDRESS     = "1779211674516000_5"
QIQ_SERVICE     = "1779211785479"
QIQ_NOTES       = "1779211674516000_7"

DATA_DIR = os.environ.get("DATA_DIR", BASE_DIR)
SEEN_LEADS_FILE  = os.path.join(DATA_DIR, "seen_leads.json")
LOCK_FILE        = os.path.join(DATA_DIR, "daemon.lock")
WEBHOOK_LOG_FILE = os.path.join(DATA_DIR, "webhook_debug.log")
CHECK_INTERVAL = 120  # every 2 minutes
WEBHOOK_PORT = int(os.environ.get("PORT", 5002))

# Generic fallback — fires for any campaign NOT listed below
AUTO_REPLY_TEMPLATE = (
    "Hey {name}! Thanks for reaching out to Clean Stream Pro Wash \U0001f4a6 "
    "We’re working on your estimate and will give you a call from (616) 377-2818 "
    "as soon as it’s ready! In the meantime if there’s anything else we should "
    "know just text us back here \U0001f601"
)

# House Washing campaign — both the original and Higher Intent form IDs
HOUSE_WASH_FORM_IDS = {
    "1246368250318759",  # Original More Volume form
    "1484216576717375",  # Higher Intent form (active)
}
HOUSE_WASH_AUTO_REPLY = (
    "Hey {name}! Thanks for reaching out to Clean Stream Pro Wash \U0001f4a6 "
    "We’re working on your estimate and will give you a call from (616) 377-2818 "
    "as soon as it’s ready! In the meantime if there’s anything else we should "
    "know just text us back here \U0001f601"
)

# Maps actual Facebook field names → display label (in desired order)
FIELD_ORDER = [
    ("what_can_we_clean_for_you",  "What Can We Clean For You"),
    ("what_can_we_clean_for_you?", "What Can We Clean For You"),
    ("first_name",                 "First Name"),
    ("last_name",                  "Last Name"),
    ("phone_number",               "Phone Number"),
    ("phone",                      "Phone Number"),
    ("email",                      "Email"),
    ("street_address",             "Street Address"),
    ("city",                       "City"),
    ("zip_code",                   "Zip Code"),
]

def load_seen_leads():
    if os.path.exists(SEEN_LEADS_FILE):
        with open(SEEN_LEADS_FILE, "r") as f:
            return set(json.load(f))
    return set()

def save_seen_leads(seen):
    with open(SEEN_LEADS_FILE, "w") as f:
        json.dump(list(seen), f)

def extract_lead_info(lead_fields):
    info = {"name": "", "phone": ""}
    for f in lead_fields:
        key = f["name"].lower().rstrip("?")
        val = f["values"][0] if f.get("values") else ""
        if key == "first_name":
            info["name"] = val
        elif key in ("phone", "phone_number"):
            info["phone"] = val
    return info

def format_lead_body(form_name, lead_fields):
    field_map = {f["name"]: f["values"][0] for f in lead_fields if f.get("values")}
    lines = ["New Lead"]
    used = set()
    for key, label in FIELD_ORDER:
        if key in field_map and key not in used:
            # Clean up underscore-formatted values (e.g. house_+_windows -> House + Windows)
            value = field_map[key].replace("_", " ").replace("+", "+").strip()
            lines.append(f"{label}: {value}")
            used.add(key)
    for key, value in field_map.items():
        if key not in used:
            label = key.rstrip("?").replace("_", " ").strip().title()
            lines.append(f"{label}: {value.replace('_', ' ')}")
    return "\n".join(lines)

def send_owner_notifications(form_name, lead_fields):
    body = format_lead_body(form_name, lead_fields)
    twilio = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    try:
        twilio.messages.create(body=body, from_=TWILIO_FROM_NUMBER, to=TWILIO_TO_NUMBER)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Owner SMS sent")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Owner SMS failed: {e}")

    try:
        msg = MIMEText(body)
        msg["Subject"] = "New Lead - Clean Stream Pro Wash"
        msg["From"] = NOTIFY_EMAIL
        msg["To"] = NOTIFY_EMAIL
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(NOTIFY_EMAIL, NOTIFY_EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Owner email sent")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Owner email failed: {e}")

def send_client_autoreply(lead_fields, form_id=None):
    info = extract_lead_info(lead_fields)
    phone = info["phone"]
    name = info["name"] or "there"
    if not phone:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] No phone number found, skipping auto-reply")
        return
    # Normalize phone to E.164
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10:
        phone = f"+1{digits}"
    elif not phone.startswith("+"):
        phone = f"+{digits}"

    template = HOUSE_WASH_AUTO_REPLY if form_id in HOUSE_WASH_FORM_IDS else AUTO_REPLY_TEMPLATE
    message = template.replace("{name}", name)
    try:
        twilio = TwilioClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        twilio.messages.create(body=message, from_=TWILIO_FROM_NUMBER, to=phone)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Auto-reply sent to {phone}")
    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Auto-reply failed: {e}")

def submit_to_quoteiq(lead_fields):
    field_map = {f["name"].lower().rstrip("?"): (f["values"][0] if f.get("values") else "") for f in lead_fields}
    address_parts = [
        field_map.get("street_address", ""),
        field_map.get("city", ""),
        field_map.get("zip_code", ""),
    ]
    address = ", ".join(p for p in address_parts if p)
    service_raw = field_map.get("what_can_we_clean_for_you", "")
    service = service_raw.replace("_", " ").replace("  ", " ").strip()
    notes = next((v for k, v in field_map.items() if "anything" in k or "know" in k or "note" in k), "")

    payload = {
        "form_id":    QUOTEIQ_FORM_ID,
        "user_id":    QUOTEIQ_USER_ID,
        "company_id": QUOTEIQ_COMPANY_ID,
        "channel_id": QUOTEIQ_CHANNEL_ID,
        "_hp": "",
        "data": {
            QIQ_FIRST_NAME: field_map.get("first_name", ""),
            QIQ_LAST_NAME:  field_map.get("last_name", ""),
            QIQ_EMAIL:      field_map.get("email", ""),
            QIQ_PHONE:      field_map.get("phone_number") or field_map.get("phone", ""),
            QIQ_ADDRESS:    address,
            QIQ_SERVICE:    service,
            QIQ_NOTES:      notes,
        }
    }
    body = json.dumps(payload).encode("utf-8")
    for attempt in range(1, 4):
        req = urllib.request.Request(
            QUOTEIQ_ENDPOINT,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                raw = resp.read().decode("utf-8")
                print(f"[{datetime.now().strftime('%H:%M:%S')}] QuoteIQ submitted: {resp.status} {raw[:100]}")
                return
        except urllib.error.HTTPError as e:
            raw = e.read().decode("utf-8")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] QuoteIQ HTTP error (attempt {attempt}/3): {e.code} {raw[:100]}")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] QuoteIQ failed (attempt {attempt}/3): {e}")
        if attempt < 3:
            time.sleep(5)

def check_for_new_leads():
    try:
        client = MetaAdsClient()
        pages = client.get_pages()
        if not pages.get("data"):
            return
        page = pages["data"][0]
        page_id = page["id"]
        page_token = page.get("access_token", client.access_token)
        page_client = MetaAdsClient(access_token=page_token)

        seen_leads = load_seen_leads()
        updated = False

        forms = page_client.get_lead_forms(page_id)
        for form in forms.get("data", []):
            form_id = form["id"]
            form_name = form.get("name", form_id)
            try:
                leads = page_client.get_form_leads(form_id)
                for lead in leads.get("data", []):
                    lead_id = lead["id"]
                    if lead_id not in seen_leads:
                        fields = lead.get("field_data", [])
                        created_str = lead.get("created_time", "")
                        try:
                            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
                            age_minutes = (datetime.now(timezone.utc) - created).total_seconds() / 60
                        except Exception:
                            age_minutes = 0
                        if age_minutes <= 10:
                            send_owner_notifications(form_name, fields)
                            send_client_autoreply(fields, form_id=form_id)
                            submit_to_quoteiq(fields)
                        else:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Skipping stale lead {lead_id} ({age_minutes:.0f} min old)")
                        seen_leads.add(lead_id)
                        updated = True
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Could not fetch leads for {form_name}: {e}")

        if updated:
            save_seen_leads(seen_leads)

    except Exception as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Lead check error: {e}")

def start_webhook_listener():
    app = Flask(__name__)
    log = app.logger
    app.logger.disabled = True
    import logging
    logging.getLogger('werkzeug').disabled = True

    @app.route('/debug-webhook', methods=['POST', 'GET'])
    def debug_webhook():
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        payload = request.get_json(silent=True) or request.form.to_dict() or request.data.decode()
        entry = {
            "timestamp": ts,
            "method": request.method,
            "headers": dict(request.headers),
            "payload": payload
        }
        with open(WEBHOOK_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        print(f"[{ts}] Webhook received: {json.dumps(payload)[:200]}", flush=True)
        return jsonify({"status": "received"}), 200

    @app.route('/health', methods=['GET'])
    def health():
        return jsonify({"status": "ok", "service": "CleanStream Daemon"}), 200

    app.run(host='0.0.0.0', port=WEBHOOK_PORT, debug=False, use_reloader=False)


ON_RAILWAY = "RAILWAY_ENVIRONMENT" in os.environ

def acquire_lock():
    # Skip lock on Railway — only one instance ever runs there
    if ON_RAILWAY:
        return
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE) as f:
            pid = f.read().strip()
        try:
            os.kill(int(pid), 0)
            print(f"Daemon already running (PID {pid}). Exiting.", flush=True)
            sys.exit(0)
        except (OSError, ValueError):
            pass  # stale lock — previous instance is gone
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

def release_lock():
    if ON_RAILWAY:
        return
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)

def main():
    acquire_lock()
    try:
        print("=" * 50, flush=True)
        print("  CLEAN STREAM - LEAD ALERT DAEMON", flush=True)
        print(f"  Checking every {CHECK_INTERVAL} seconds", flush=True)
        print(f"  Webhook listener on port {WEBHOOK_PORT}", flush=True)
        print("=" * 50, flush=True)

        webhook_thread = threading.Thread(target=start_webhook_listener, daemon=True)
        webhook_thread.start()

        while True:
            check_for_new_leads()
            time.sleep(CHECK_INTERVAL)
    finally:
        release_lock()

if __name__ == "__main__":
    main()
