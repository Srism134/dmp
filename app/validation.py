import json
import os
import logging
from jsonschema import validate, ValidationError

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "..", "schemas", "dmp_v1.json")

with open(SCHEMA_PATH, "r") as f:
    DMP_SCHEMA = json.load(f)

def validate_dmp(data: dict):
    try:
        validate(instance=data, schema=DMP_SCHEMA)
        return True, None
    except ValidationError as e:
        logging.warning("DMP schema validation failed: %s", e)  # <— log
        return False, str(e)
