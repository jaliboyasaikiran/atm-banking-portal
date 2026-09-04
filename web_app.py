import json
import math
import os
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
WEB_ROOT = Path(__file__).parent / "web"

state = {
    "balance": 10000,
    "card_number": "8328679614",
    "pin": "1234",
    "logged_in": False,
    "failed_attempts": 0,
    "locked": False,
    "atm_notes": {2000: 5, 500: 10, 200: 20, 100: 50},
    "daily_withdrawal": 0,
    "withdrawal_date": date.today(),
    "transactions": [],
}


class AtmHandler(BaseHTTPRequestHandler):
    def send_json(self, status, data):
        payload = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        return json.loads(self.rfile.read(length) or b"{}")

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.serve_file("index.html", "text/html; charset=utf-8")
        elif self.path == "/styles.css":
            self.serve_file("styles.css", "text/css; charset=utf-8")
        elif self.path == "/app.js":
            self.serve_file("app.js", "text/javascript; charset=utf-8")
        elif self.path == "/api/status":
            self.send_json(200, self.status_response())
        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        try:
            data = self.read_json()
        except (json.JSONDecodeError, ValueError):
            self.send_json(400, {"error": "Invalid JSON request"})
            return

        if self.path == "/api/login":
            self.login(data)
        elif self.path == "/api/action":
            self.action(data)
        else:
            self.send_json(404, {"error": "Not found"})

    def login(self, data):
        if state["locked"]:
            self.send_json(423, {"error": "Card locked after three incorrect attempts"})
            return

        card_number = str(data.get("card_number", "")).replace(" ", "")
        if card_number != state["card_number"] or str(data.get("pin", "")) != state["pin"]:
            state["failed_attempts"] += 1
            if state["failed_attempts"] >= 3:
                state["locked"] = True
                self.send_json(423, {"error": "Card locked after three incorrect attempts"})
            else:
                remaining = 3 - state["failed_attempts"]
                self.send_json(401, {"error": f"Incorrect card number or PIN. {remaining} attempts remaining"})
            return

        state["failed_attempts"] = 0
        state["logged_in"] = True
        self.send_json(200, self.status_response())

    def action(self, data):
        if not state["logged_in"]:
            self.send_json(401, {"error": "Please enter your PIN first"})
            return

        action = data.get("action")
        if action == "balance":
            self.send_json(200, self.status_response())
        elif action == "statement":
            self.send_json(200, {"transactions": state["transactions"][-10:]})
        elif action == "withdraw":
            self.change_balance(data.get("amount", 0), "Withdrawal successful", withdrawing=True)
        elif action == "deposit":
            self.change_balance(data.get("amount", 0), "Deposit successful")
        elif action == "change_pin":
            self.change_pin(data)
        elif action == "logout":
            state["logged_in"] = False
            self.send_json(200, {"message": "You have been logged out"})
        else:
            self.send_json(400, {"error": "Unknown action"})

    def change_balance(self, amount, message, withdrawing=False):
        if (
            not isinstance(amount, (int, float))
            or isinstance(amount, bool)
            or not math.isfinite(amount)
            or amount <= 0
        ):
            self.send_json(400, {"error": "Enter a valid amount"})
        elif amount < 500:
            self.send_json(400, {"error": "The minimum amount is 500"})
        elif withdrawing and amount % 100 != 0:
            self.send_json(400, {"error": "Withdrawal amount must be in ₹100 multiples"})
        elif withdrawing and not self.can_withdraw(amount):
            return
        else:
            if withdrawing:
                notes = self.dispense_notes(amount)
                if notes is None:
                    self.send_json(400, {"error": "ATM cannot dispense that exact amount"})
                    return
                state["balance"] -= amount
                state["daily_withdrawal"] += amount
                for note, count in notes.items():
                    state["atm_notes"][note] -= count
                details = ", ".join(f"{count} x ₹{note}" for note, count in notes.items() if count)
                message = f"{message} ({details})"
            else:
                state["balance"] += amount
            self.record_transaction("Withdrawal" if withdrawing else "Deposit", amount)
            self.send_json(200, {"message": message, **self.status_response()})

    def can_withdraw(self, amount):
        self.reset_daily_limit()
        if amount > state["balance"]:
            self.send_json(400, {"error": "Insufficient balance"})
            return False
        if amount > sum(note * count for note, count in state["atm_notes"].items()):
            self.send_json(400, {"error": "ATM does not have enough cash"})
            return False
        remaining = 20000 - state["daily_withdrawal"]
        if amount > remaining:
            self.send_json(400, {"error": f"Daily withdrawal limit exceeded. Remaining: ₹{remaining}"})
            return False
        return True

    def dispense_notes(self, amount):
        amount = int(amount)
        remaining = amount
        notes = {}
        for note in sorted(state["atm_notes"], reverse=True):
            count = int(min(remaining // note, state["atm_notes"][note]))
            if count:
                notes[note] = count
                remaining -= note * count
        return notes if remaining == 0 else None

    def reset_daily_limit(self):
        if state["withdrawal_date"] != date.today():
            state["withdrawal_date"] = date.today()
            state["daily_withdrawal"] = 0

    def record_transaction(self, transaction_type, amount):
        state["transactions"].append({
            "type": transaction_type,
            "amount": amount,
            "balance": state["balance"],
            "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        })

    def change_pin(self, data):
        current_pin = str(data.get("current_pin", ""))
        new_pin = str(data.get("new_pin", ""))
        if current_pin != state["pin"]:
            self.send_json(400, {"error": "Incorrect current PIN"})
        elif len(new_pin) != 4 or not new_pin.isdigit():
            self.send_json(400, {"error": "New PIN must contain four digits"})
        else:
            state["pin"] = new_pin
            self.send_json(200, {"message": "PIN changed successfully"})

    def status_response(self):
        self.reset_daily_limit()
        return {
            "logged_in": state["logged_in"],
            "balance": state["balance"],
            "card_number": state["card_number"],
            "daily_withdrawal": state["daily_withdrawal"],
            "daily_limit": 20000,
            "atm_cash": sum(note * count for note, count in state["atm_notes"].items()),
        }

    def serve_file(self, filename, content_type):
        file_path = WEB_ROOT / filename
        try:
            payload = file_path.read_bytes()
        except FileNotFoundError:
            self.send_json(404, {"error": "Frontend file not found"})
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format_string, *args):
        print(f"{self.address_string()} - {format_string % args}")


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), AtmHandler)
    browser_host = "localhost" if HOST in {"0.0.0.0", "::"} else HOST
    print(f"ATM web app running at http://{browser_host}:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nATM web app stopped.")
    finally:
        server.server_close()
