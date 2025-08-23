# app/dmp.py
import os, json
import xml.etree.ElementTree as ET
from .db import get_db  # <- we only call this inside functions

def _fetch(conn, sql, params=()):
    c = conn.execute(sql, params)
    cols = [d[0] for d in c.description]
    return [dict(zip(cols, r)) for r in c.fetchall()]

def build_dmp(conn, patient_guid: str):
    # --- patient ---
    rows = _fetch(conn, """
        SELECT PatientGuid, Forenames, Surname, Sex, PostCode, DateOfBirth
        FROM patients
        WHERE PatientGuid = ?
    """, (patient_guid,))
    if not rows:
        return None
    p = rows[0]

    # --- medications ---  (alias your schema columns to exporter keys)
    meds = _fetch(conn, """
        SELECT
            MedicationGuid,
            Term,
            Dosage,
            COALESCE(EffectiveDateTime, IssuedDate, '') AS StartDate,
            COALESCE(DrugStatus, Status, 1)            AS Status,
            PrescriptionType
        FROM medications
        WHERE PatientGuid = ?
        ORDER BY StartDate DESC
    """, (patient_guid,))

    # --- appointments ---
    appts = _fetch(conn, """
        SELECT
            AppointmentGuid,
            StartDateTime,
            EndDateTime,
            CurrentStatus AS Status,
            SessionLocation AS Location
        FROM appointments
        WHERE PatientGuid = ?
        ORDER BY StartDateTime DESC
    """, (patient_guid,))

    # --- events ---
    events = _fetch(conn, """
        SELECT
            EventGuid,
            EventType,
            Term,
            ReadCode,
            SnomedCTCode,
            EffectiveDateTime
        FROM events
        WHERE PatientGuid = ?
        ORDER BY EffectiveDateTime DESC
    """, (patient_guid,))

    # Split allergies/immunisations (EventType 11, 13)
    allergies      = [e for e in events if e.get("EventType") == 11]
    immunisations  = [e for e in events if e.get("EventType") == 13]

    # Minimal top-level DMP object (v1)
    return {
        "PatientGuid": p["PatientGuid"],
        "Name": f'{(p.get("Forenames") or "").strip()} {(p.get("Surname") or "").strip()}'.strip(),
        "DOB": p.get("DateOfBirth", ""),
        "Sex": p.get("Sex", ""),
        "PostCode": p.get("PostCode", ""),
        "Medications": meds,
        "Appointments": appts,
        "Events": events,
        "Allergies": allergies,
        "Immunisations": immunisations,
    }

def export_dmp_json(patient_guid: str, save: bool = False, outdir: str = "data/exports"):
    conn = get_db()
    dmp = build_dmp(conn, patient_guid)
    if not dmp:
        return None, "not_found"
    text = json.dumps(dmp, ensure_ascii=False, indent=2, default=str)
    path = None
    if save:
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, f"{patient_guid}.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    return text, path

def _dict_to_xml(tag: str, data):
    elem = ET.Element(tag)
    if isinstance(data, dict):
        for k, v in data.items():
            child = _dict_to_xml(k, v)
            elem.append(child)
    elif isinstance(data, list):
        for item in data:
            child = _dict_to_xml("item", item)
            elem.append(child)
    else:
        # scalar
        elem.text = "" if data is None else str(data)
    return elem

def export_dmp_xml(patient_guid: str, save: bool = False, outdir: str = "data/exports"):
    text, _ = export_dmp_json(patient_guid, save=False)
    if text is None:
        return None, "not_found"
    obj = json.loads(text)
    root = _dict_to_xml("DigitalMedicalPassport", obj)
    xml_bytes = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    path = None
    if save:
        os.makedirs(outdir, exist_ok=True)
        path = os.path.join(outdir, f"{patient_guid}.xml")
        with open(path, "wb") as f:
            f.write(xml_bytes)
    return xml_bytes.decode("utf-8"), path

def import_dmp_json(payload: dict):
    """
    MVP: validate via JSON Schema (if available) and return PatientGuid.
    """
    # Optional schema validation
    try:
        from .validation import validate_dmp_json as _validate
        _validate(payload)
    except Exception as e:
        # Let routes decide to 400 on this error
        raise

    # (No DB merge yet in MVP)
    return {"patientGuid": payload.get("PatientGuid")}
