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