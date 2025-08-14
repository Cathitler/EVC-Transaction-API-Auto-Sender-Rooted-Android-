from flask import Flask, request, jsonify
from datetime import datetime
import re
import json
import os
import unicodedata
import uuid

app = Flask(__name__)
HORMUUD_NUMBER = "192"
JSON_FILE = "evc_messages.json"

# Ensure JSON file exists
if not os.path.exists(JSON_FILE):
    with open(JSON_FILE, "w") as f:
        json.dump([], f)

def normalize_number(number: str) -> str:
    """Remove invisible/control unicode characters"""
    number = number.strip()
    return "".join(ch for ch in number if unicodedata.category(ch)[0] != "C")

def clean_float(value: str) -> float:
    """Remove non-numeric characters except dot, fix trailing dot"""
    value = re.sub(r"[^\d\.]", "", value)
    if value.endswith("."):
        value = value[:-1]
    return float(value)

@app.route("/", methods=["GET", "POST"])
def parse_message():
    text = request.args.get("text", "").strip()
    sender_number = normalize_number(request.args.get("title", ""))

    # Ignore messages not from Hormuud
    if sender_number != HORMUUD_NUMBER:
        result = {"type": "ignored", "message": "Not from Hormuud"}
        print(json.dumps(result, indent=4))
        return jsonify(result), 200

    parsed = {"type": "other", "message": text}

    # ----- RECEIVE -----
    if "ka heshay" in text:
        m = re.search(
            r"waxaad \$([\d\.]+)\s+ka heshay\s+(\d+),?\s*Tar:\s*([\d/]+)\s+([\d:]+),?\s*haraagagu waa \$([\d\.]+)",
            text, re.IGNORECASE
        )
        if m:
            try:
                parsed = {
                    "id": str(uuid.uuid4()),
                    "type": "received",
                    "amount": float(m.group(1)),
                    "counterparty": m.group(2),
                    "transaction_datetime": datetime.strptime(
                        f"{m.group(3)} {m.group(4)}", "%d/%m/%y %H:%M:%S"
                    ).isoformat(),
                    "new_balance": clean_float(m.group(5))
                }
            except Exception as e:
                parsed = {"type": "error", "message": str(e)}

    # ----- SEND -----
    elif "ayaad uwareejisay" in text:
        m = re.search(
            r"\$([\d\.]+)\s+ayaad uwareejisay\s+(\d+),?\s*Tar:\s*([\d/]+)\s+([\d:]+),?\s*Haraagaagu waa \$([\d\.]+)",
            text, re.IGNORECASE
        )
        if m:
            try:
                parsed = {
                    "id": str(uuid.uuid4()),
                    "type": "send",
                    "amount": float(m.group(1)),
                    "counterparty": m.group(2),
                    "transaction_datetime": datetime.strptime(
                        f"{m.group(3)} {m.group(4)}", "%d/%m/%y %H:%M:%S"
                    ).isoformat(),
                    "new_balance": clean_float(m.group(5))
                }
            except Exception as e:
                parsed = {"type": "error", "message": str(e)}

    # ----- Save to JSON file -----
    try:
        with open(JSON_FILE, "r+") as f:
            data = json.load(f)
            data.append(parsed)
            f.seek(0)
            json.dump(data, f, indent=4)
    except Exception as e:
        print("Error saving to JSON:", e)

    # Print parsed JSON to terminal
    print("Parsed message:", json.dumps(parsed, indent=4))
    return jsonify(parsed), 200


# Endpoint to view all saved transactions
@app.route("/transactions", methods=["GET"])
def get_transactions():
    try:
        with open(JSON_FILE, "r") as f:
            data = json.load(f)
        return jsonify(data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)