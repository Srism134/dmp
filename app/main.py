# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Header
import sqlite3

API_KEY = "secret123"  # dummy token for Phase 4

# ------------ security ------------
def require_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")

# ------------ db helpers ------------
def get_db():
    conn = sqlite3.connect("medical.db")
    conn.row_factory = sqlite3.Row
    return conn

def patient_fk(conn) -> str:
    """Return the FK column name used in child tables."""
    # prefer 'patient_id', else 'PatientGuid', else 'patientGuid'
    for col in ("patient_id", "PatientGuid", "patientGuid"):
        try:
            conn.execute(f"SELECT 1 FROM Patients LIMIT 1")  # table exists
            # does Patients have this column?
            cols = [r[1] for r in conn.execute("PRAGMA table_info(Patients)")]
            if col in cols or col == "patient_id":
                return col if col in cols else "patient_id"
        except Exception:
            pass
    return "patient_id"

def patient_cols(conn):
    """Return a tuple: (id_col, name_cols list) for Patients table."""
    cols = [r[1] for r in conn.execute("PRAGMA table_info(Patients)")]
    if {"PatientGuid","FirstName","LastName","DateOfBirth"}.issubset(set(cols)):
        return "PatientGuid", ["FirstName","LastName","DateOfBirth"]
    # default to our schema
    return "patient_id", ["name","dob","gender"]

# ------------ app ------------
app = FastAPI(title="DMP API")

@app.get("/health")
def health():
    return {"status": "ok"}

# GET /patients – list
@app.get("/patients")
def list_patients(_=Depends(require_api_key)):
    conn = get_db()
    id_col, extra = patient_cols(conn)  # id + visible fields
    cols = ", ".join([id_col] + extra)
    rows = conn.execute(f"SELECT {cols} FROM Patients LIMIT 50").fetchall()
    conn.close()
    out = []
    for r in rows:
        item = {id_col: r[id_col]}
        for c in extra:
            item[c] = r[c]
        out.append(item)
    return out

# GET /patients/{guid}
@app.get("/patients/{guid}")
def patient_detail(guid: str, _=Depends(require_api_key)):
    conn = get_db()
    id_col, extra = patient_cols(conn)
    cols = ", ".join([id_col] + extra)
    row = conn.execute(f"SELECT {cols} FROM Patients WHERE {id_col}=?", (guid,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(404, "Patient not found")
    return {c: row[c] for c in [id_col] + extra}

# GET /patients/{guid}/appointments
@app.get("/patients/{guid}/appointments")
def patient_appointments(guid: str, _=Depends(require_api_key)):
    conn = get_db()
    fk = patient_fk(conn)
    rows = conn.execute(
        f"SELECT appointment_id, date, doctor, reason FROM Appointments WHERE {fk}=? ORDER BY date DESC",
        (guid,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# GET /patients/{guid}/medications
@app.get("/patients/{guid}/medications")
def patient_medications(guid: str, _=Depends(require_api_key)):
    conn = get_db()
    fk = patient_fk(conn)
    rows = conn.execute(
        f"""SELECT medication_id, drug_name, dose, start_date, end_date
            FROM Medications WHERE {fk}=?
            ORDER BY COALESCE(start_date, end_date) DESC""",
        (guid,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# GET /patients/{guid}/events
@app.get("/patients/{guid}/events")
def patient_events(guid: str, _=Depends(require_api_key)):
    conn = get_db()
    fk = patient_fk(conn)
    # support either schema: (event_type, description, date) or (type, details, date)
    cols = [r[1] for r in conn.execute("PRAGMA table_info(Events)")]
    ev_type = "event_type" if "event_type" in cols else "type"
    desc    = "description" if "description" in cols else ("details" if "details" in cols else "description")
    rows = conn.execute(
        f"SELECT event_id, {ev_type} AS event_type, {desc} AS description, date FROM Events WHERE {fk}=? ORDER BY date DESC",
        (guid,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
