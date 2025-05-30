Got it! If you want to **use Firebase Firestore via REST API or Firebase Client SDK** without the admin SDK (which requires service account and admin privileges), and you provide the Firebase config (like API key, project ID, auth domain, etc.), then the flow is different.

Firebase Admin SDK is typically used on backend with full privileges. But if you want to do basic create/read/update/delete (CRUD) operations on Firestore from Python **without admin SDK**, you’ll have to use Firebase REST API or the Firebase Client SDK (usually JavaScript).

---

### Here’s a **simplified version of the MD file** assuming:

* You will use **Firebase Firestore REST API** or Python HTTP client to call Firebase endpoints.
* You have Firebase config (API key, project id, etc.).
* You do NOT want to use admin SDK or service account keys.
* You will handle auth (for example, Firebase Authentication tokens) separately or your Firestore rules allow unauthenticated access (not recommended for production).

---

# License Key Server with Python + Firebase Firestore (No Admin SDK)

## Overview

This backend License Key Manager uses Python with Firebase Firestore REST API.

You can:

* Create license keys
* Check license key validity
* Delete (deactivate) license keys

---

## Prerequisites

* Firebase project with Firestore enabled
* Firebase Web API Key and Project ID
* Python 3 and `requests` library

---

## Setup

### Install Python dependencies

```bash
pip install requests flask
```

### Project structure

```
license-server/
│
├── app.py
├── firebase_config.py
└── requirements.txt
```

---

## firebase\_config.py

```python
FIREBASE_API_KEY = "your_api_key_here"
FIREBASE_PROJECT_ID = "your_project_id_here"
FIREBASE_DATABASE_URL = f"https://firestore.googleapis.com/v1/projects/{FIREBASE_PROJECT_ID}/databases/(default)/documents"
```

---

## app.py

```python
from flask import Flask, request, jsonify
import requests
import secrets
from datetime import datetime, timedelta
import json

from firebase_config import FIREBASE_API_KEY, FIREBASE_DATABASE_URL

app = Flask(__name__)

COLLECTION = "licenses"

def get_firestore_url(doc_id=None):
    if doc_id:
        return f"{FIREBASE_DATABASE_URL}/{COLLECTION}/{doc_id}"
    else:
        return f"{FIREBASE_DATABASE_URL}/{COLLECTION}"

def to_firestore_format(data: dict):
    # Converts python dict to Firestore REST API format
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
            # Add more types as needed
            fs_data["fields"][k] = {"stringValue": str(v)}
    return fs_data

def from_firestore_format(doc):
    # Converts Firestore response to normal dict
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
        # Optionally update status to inactive (requires PATCH)
        return jsonify({"valid": False, "message": "License key expired"}), 403

    return jsonify({"valid": True, "message": "License key valid", "expiresAt": data["expiresAt"]}), 200

@app.route('/delete/<license_key>', methods=['DELETE'])
def delete_license(license_key):
    url = get_firestore_url(license_key)
    params = {"key": FIREBASE_API_KEY}

    # Update status to inactive
    patch_data = to_firestore_format({"status": "inactive"})

    res = requests.patch(url, params=params, json=patch_data)

    if res.status_code != 200:
        return jsonify({"error": res.text}), 500

    return jsonify({"success": True, "message": "License key deactivated"}), 200

if __name__ == '__main__':
    app.run(debug=True)
```

---

## Notes:

* Firestore REST API requires your Firestore rules to allow access via your API key or you must pass an auth token.
* The REST API URLs and payloads must follow Firestore's specs exactly.
* This example uses PATCH to create/update documents with a specified document ID (the license key).
* For production, secure your API keys and set proper Firestore security rules.
* You can improve error handling, add authentication, and logging as needed.

---

If you want, I can help you write the exact Firestore security rules or improve the example.

