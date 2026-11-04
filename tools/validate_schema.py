
#!/usr/bin/env python3
import sys, json, pathlib, argparse
def load_json(p):
    return json.loads(pathlib.Path(p).read_text())
def validate(s_path, d_path):
    schema = load_json(s_path)
    doc = load_json(d_path)
    try:
        import jsonschema
        jsonschema.validate(doc, schema)
        print(f"SCHEMA-OK: {d_path} conforms to {s_path}")
        return True
    except ImportError:
        required = schema.get("required", [])
        missing = [f for f in required if f not in doc]
        if missing:
            print(f"SCHEMA-FAIL: missing {missing}", file=sys.stderr)
            return False
        print(f"SCHEMA-OK (fallback): {d_path}")
        return True
    except Exception as e:
        print(f"SCHEMA-FAIL: {e}", file=sys.stderr)
        return False
if __name__ == "__main__":
    pa = argparse.ArgumentParser()
    pa.add_argument("schema")
    pa.add_argument("document")
    a = pa.parse_args()
    sys.exit(0 if validate(a.schema, a.document) else 1)
