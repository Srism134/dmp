# app/validation.py
import json, re
from datetime import datetime
from dateutil.parser import isoparse
from jsonschema import Draft202012Validator
from lxml import etree

# Load JSON schema once (schemas/dmp_v1.json)
with open("schemas/dmp_v1.json", "r", encoding="utf-8") as f:
    DMP_SCHEMA = json.load(f)

DMP_VALIDATOR = Draft202012Validator(DMP_SCHEMA)
UUID_RE = re.compile(r"^[0-9a-fA-F-]{36}$")

def validate_guid(val: str, field: str, errors: list):
    if not isinstance(val, str) or not UUID_RE.match(val):
        errors.append(f"{field}: invalid GUID")

def validate_date(val: str, field: str, errors: list, allow_date_only=False):
    if not isinstance(val, str):
        errors.append(f"{field}: must be string")
        return
    try:
        # allow YYYY-MM-DD if allow_date_only True, otherwise ISO datetime
        if allow_date_only and re.fullmatch(r"\d{4}-\d{2}-\d{2}", val):
            datetime.strptime(val, "%Y-%m-%d")
        else:
            isoparse(val)  # robust ISO parser
    except Exception:
        errors.append(f"{field}: invalid ISO date/datetime '{val}'")

def validate_lookup(val, field, allowed, errors):
    if val not in allowed:
        # keep error short & readable
        allowed_sorted = sorted(list(allowed))
        errors.append(f"{field}: '{val}' is not in {allowed_sorted}")

def validate_dmp_json(bundle: dict, lookup_sets=None) -> list:
    """
    Returns a list of error strings. Empty => valid.
    lookup_sets: optional dict with allowed sets for coded values
                 e.g. {'sex': {'F','M','U','I'}, 'event_type': {1,11,13}, ...}
    """
    errors = []

    # 1) JSON Schema structure/required fields
    for err in sorted(DMP_VALIDATOR.iter_errors(bundle), key=lambda e: e.path):
        path = ".".join([str(x) for x in err.path]) or "(root)"
        errors.append(f"schema: {path}: {err.message}")

    if errors:
        return errors  # stop early if structure fails

    # 2) Field-level checks & lookups
    p = bundle["patient"]
    validate_guid(p["PatientGuid"], "patient.PatientGuid", errors)
    validate_date(p["DateOfBirth"], "patient.DateOfBirth", errors, allow_date_only=True)
    if lookup_sets and "sex" in lookup_sets:
        validate_lookup(p["Sex"], "patient.Sex", lookup_sets["sex"], errors)

    for i, a in enumerate(bundle["appointments"]):
        validate_guid(a["AppointmentGuid"], f"appointments[{i}].AppointmentGuid", errors)
        validate_date(a["StartDateTime"], f"appointments[{i}].StartDateTime", errors)
        validate_date(a["EndDateTime"], f"appointments[{i}].EndDateTime", errors)

    for i, m in enumerate(bundle["medications"]):
        validate_guid(m["MedicationGuid"], f"medications[{i}].MedicationGuid", errors)
        validate_date(m["EffectiveDateTime"], f"medications[{i}].EffectiveDateTime", errors)
        if lookup_sets:
            if "prescription_type" in lookup_sets:
                validate_lookup(m["PrescriptionType"], f"medications[{i}].PrescriptionType", lookup_sets["prescription_type"], errors)
            if "drug_status" in lookup_sets:
                validate_lookup(m["DrugStatus"], f"medications[{i}].DrugStatus", lookup_sets["drug_status"], errors)

    for i, ev in enumerate(bundle["events"]):
        validate_guid(ev["EventGuid"], f"events[{i}].EventGuid", errors)
        validate_date(ev["EffectiveDateTime"], f"events[{i}].EffectiveDateTime", errors)
        if lookup_sets and "event_type" in lookup_sets:
            validate_lookup(ev["EventType"], f"events[{i}].EventType", lookup_sets["event_type"], errors)

    return errors

# Optional: very light XML validation (well-formed check)
def validate_dmp_xml_text(xml_text: str) -> list:
    errors = []
    try:
        etree.fromstring(xml_text.encode("utf-8"))
    except Exception as e:
        errors.append(f"xml: not well-formed: {e}")
    return errors
