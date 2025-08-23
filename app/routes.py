# app/routes.py
from flask import Blueprint, jsonify, request, current_app
from .auth import require_api_key
from .db import get_db
from .dmp import export_dmp_json, export_dmp_xml, import_dmp_json

api = Blueprint("api", __name__)

# --- Health ---
@api.get("/health")
def health():
    return jsonify(status="ok", message="API is working")

# --- Patients list (paging + simple search) ---
@api.get("/patients")
@require_api_key
def list_patients():
    db = get_db()

    # paging
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        limit = 20
    try:
        offset = int(request.args.get("offset", 0))
    except ValueError:
        offset = 0

    # optional search by name fragment
    q = request.args.get("q", "").strip()

    params = []
    where = ""
    if q:
        where = "WHERE (Surname LIKE ? OR Forenames LIKE ?)"
        frag = f"%{q}%"
        params.extend([frag, frag])

    total = db.execute(f"SELECT COUNT(*) AS c FROM patients {where}", params).fetchone()["c"]

    params.extend([limit, offset])
    rows = db.execute(
        f"""
        SELECT PatientGuid, Forenames, Surname, DateOfBirth, Sex, PostCode
        FROM patients
        {where}
        ORDER BY Surname, Forenames
        LIMIT ? OFFSET ?
        """,
        params,
    ).fetchall()

    items = [dict(r) for r in rows]
    return jsonify(items=items, paging={"limit": limit, "offset": offset, "total": total})

# --- Single patient details ---
@api.get("/patients/<guid>")
@require_api_key
def get_patient(guid):
    db = get_db()
    row = db.execute(
        """
        SELECT PatientGuid, Forenames, Surname, DateOfBirth, Sex, PostCode
        FROM patients
        WHERE PatientGuid = ?
        """,
        (guid,),
    ).fetchone()
    if not row:
        return jsonify(error="Not found"), 404
    return jsonify(dict(row))

# --- Patient appointments ---
@api.get("/patients/<guid>/appointments")
@require_api_key
def patient_appointments(guid):
    db = get_db()
    rows = db.execute(
        """
        SELECT AppointmentGuid, PatientGuid, StartDateTime, EndDateTime, CurrentStatus, SessionLocation
        FROM appointments
        WHERE PatientGuid = ?
        ORDER BY StartDateTime DESC
        """,
        (guid,),
    ).fetchall()
    return jsonify([dict(r) for r in rows])

# --- Patient medications ---
@api.get("/patients/<guid>/medications")
@require_api_key
def patient_medications(guid):
    db = get_db()
    rows = db.execute(
        """
        SELECT MedicationGuid, PatientGuid, Term, Dosage, PrescriptionType, DrugStatus, EffectiveDateTime
        FROM medications
        WHERE PatientGuid = ?
        ORDER BY EffectiveDateTime DESC
        """,
        (guid,),
    ).fetchall()
    return jsonify([dict(r) for r in rows])

# --- Patient events (obs/allergies/immunisations etc.) ---
@api.get("/patients/<guid>/events")
@require_api_key
def patient_events(guid):
    db = get_db()
    rows = db.execute(
        """
        SELECT EventGuid, PatientGuid, EventType, Term, ReadCode, SnomedCTCode, EffectiveDateTime
        FROM events
        WHERE PatientGuid = ?
        ORDER BY EffectiveDateTime DESC
        """,
        (guid,),
    ).fetchall()
    return jsonify([dict(r) for r in rows])

# --- DMP export (JSON/XML) ---
@api.get("/patients/<guid>/dmp")
@require_api_key
def export_dmp(guid):
    fmt = (request.args.get("format") or "json").lower()
    save = request.args.get("save") in ("1", "true", "yes")

    try:
        if fmt == "xml":
            xml_str, saved_path = export_dmp_xml(guid, save=save)
            return (xml_str, 200, {"Content-Type": "application/xml"})
        else:
            payload, saved_path = export_dmp_json(guid, save=save)
            # If saved, include where it was written
            if save and saved_path:
                payload["_saved"] = saved_path
            return jsonify(payload)
    except Exception as ex:
        current_app.logger.exception("export failed")
        return jsonify(error=f"export failed: {type(ex).__name__}: {ex}"), 500

# --- DMP import (JSON only for MVP) ---
@api.post("/import")
def import_dmp():
    # Optional: protect with API key too. Uncomment next line if you want.
    # require_api_key(lambda: None)()  # or decorate with @require_api_key

    try:
        data = request.get_json(force=True, silent=False)
    except Exception:
        return jsonify(error="Invalid JSON"), 400

    ok, res = import_dmp_json(data)
    if not ok:
        return jsonify(error=res.get("error", "import failed"), details=res), 400

    return jsonify(message="DMP imported successfully", patientGuid=res["patientGuid"])
