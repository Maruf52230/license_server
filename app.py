from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import secrets
from datetime import datetime, timedelta

from firebase_config import FIREBASE_API_KEY, FIREBASE_DATABASE_URL

app = Flask(__name__)
CORS(app)

COLLECTION = "licenses"

def get_firestore_url(doc_id=None):
    if doc_id:
        return f"{FIREBASE_DATABASE_URL}/{COLLECTION}/{doc_id}.json"
    else:
        return f"{FIREBASE_DATABASE_URL}/{COLLECTION}.json"

def to_firestore_format(data: dict):
    fs_data = {"fields": {}}
    for k, v in data.items():
        if isinstance(v, str):
            fs_data["fields"][k] = {"stringValue": v}
        elif isinstance(v, bool):
            fs_data["fields"][k] = {"booleanValue": v}
        elif isinstance(v, int):
            fs_data["fields"][k] = {"integerValue": str(v)}
        elif isinstance(v, float):
            fs_data["fields"][k] = {"doubleValue": v}
        elif isinstance(v, datetime):
            fs_data["fields"][k] = {"timestampValue": v.isoformat() + "Z"}
        else:
            fs_data["fields"][k] = {"stringValue": str(v)}
    return fs_data

def from_firestore_format(doc):
    fields = doc.get("fields", {})
    result = {}
    for k, v in fields.items():
        if "stringValue" in v:
            result[k] = v["stringValue"]
        elif "booleanValue" in v:
            result[k] = v["booleanValue"]
        elif "integerValue" in v:
            result[k] = int(v["integerValue"])
        elif "doubleValue" in v:
            result[k] = float(v["doubleValue"])
        elif "timestampValue" in v:
            result[k] = v["timestampValue"]
        else:
            result[k] = None
    return result

def generate_license_key(length=16):
    return secrets.token_hex(length // 2).upper()

@app.route('/create', methods=['POST'])
def create_license():
    expires_in_days = request.json.get("expires_in_days", 30)

    key = generate_license_key()
    now = datetime.utcnow()
    expires_at = now + timedelta(days=expires_in_days)

    license_data = {
        "key": key,
        "status": "active",
        "createdAt": now,
        "expiresAt": expires_at,
    }

    fs_data = to_firestore_format(license_data)

    url = get_firestore_url(key)
    params = {"key": FIREBASE_API_KEY}
    res = requests.patch(url, params=params, json=fs_data)

    if res.status_code == 200:
        return jsonify({"license_key": key, "expiresAt": expires_at.isoformat()}), 201
    else:
        return jsonify({"error": res.text}), 500

@app.route('/check/<license_key>', methods=['GET'])
def check_license(license_key):
    url = get_firestore_url(license_key)
    params = {"key": FIREBASE_API_KEY}
    res = requests.get(url, params=params)

    if res.status_code == 404:
        return jsonify({"valid": False, "message": "License key not found"}), 404

    if res.status_code != 200:
        return jsonify({"error": res.text}), 500

    data = from_firestore_format(res.json())

    if data.get("status") != "active":
        return jsonify({"valid": False, "message": "License key inactive"}), 403

    now = datetime.utcnow()
    expires_at = datetime.fromisoformat(data["expiresAt"].replace("Z",""))

    if expires_at < now:
        return jsonify({"valid": False, "message": "License key expired"}), 403

    return jsonify({"valid": True, "message": "License key valid", "expiresAt": data["expiresAt"]}), 200

@app.route('/delete/<license_key>', methods=['DELETE'])
def delete_license(license_key):
    url = get_firestore_url(license_key)
    params = {"key": FIREBASE_API_KEY}

    patch_data = to_firestore_format({"status": "inactive"})

    res = requests.patch(url, params=params, json=patch_data)

    if res.status_code != 200:
        return jsonify({"error": res.text}), 500

    return jsonify({"success": True, "message": "License key deactivated"}), 200

if __name__ == '__main__':
    app.run(debug=True)