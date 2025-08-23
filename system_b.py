# system_b.py — Importer + Round-trip Export (SQLite)
from fastapi import FastAPI, Depends, HTTPException, Header
from typing import Dict, Any
import sqlite3

app = FastAPI()
DUMMY_TOKEN = "dev-token"

# ---------- Auth ----------
def auth(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Unauthorized")
    if authorization.split()[1] != DUMMY_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")

# ---------- DB helpers ----------
DB_FILE = "medical_import.db"

def _conn(db_file: str = DB_FILE):
    return sqlite3.connect(db_file, check_same_thread=False)

def ensure_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS patients(
            id TEXT PRIMARY KEY,
            name TEXT,
            birth_date TEXT
        );
    """)
    conn.commit()

def get_patient(conn, pid: str):
    cur = conn.cursor()
    cur.execute("SELECT id, name, birth_date FROM patients WHERE id = ?", (pid,))
    row = cur.fetchone()
    return row  # (id, name, birth_date) or None

# ---------- Health (for quick ping) ----------
@app.get("/health")
def health(_=Depends(auth)):
    return {"ok": True}

# ---------- Import endpoint (JSON from System A) ----------
@app.post("/import/passport")
def import_passport(payload: Dict[str, Any], _=Depends(auth)):
    """
    Accepts a DMP JSON from System A and writes minimal patient info to SQLite.
    Expected shape (minimal):
    {
      "patient": {
        "resourceType": "Patient",
        "id": "P-001",
        "name": [{"text": "Patient P-001"}],
        "birthDate": "1985-03-18"
      },
      "medications": [],
      "immunizations": [],
      "encounters": [],
      "observations": []
    }
    """
    patient = payload.get("patient", {})
    if not patient:
        raise HTTPException(status_code=422, detail="Missing 'patient' in payload")

    pid = patient.get("id", "").strip()
    if not pid:
        raise HTTPException(status_code=422, detail="Missing patient.id")

    # derive a display name if FHIR-style name array exists
    name = ""
    if isinstance(patient.get("name"), list) and patient["name"]:
        name = str(patient["name"][0].get("text", "")).strip()
    else:
        name = str(patient.get("name", "")).strip()

    birth = str(patient.get("birthDate", "")).strip()

    conn = _conn()
    ensure_tables(conn)
    conn.execute(
        "INSERT OR REPLACE INTO patients(id, name, birth_date) VALUES (?, ?, ?)",
        (pid, name, birth),
    )
    conn.commit()
    return {"status": "imported", "patient": pid}

# ---------- Stats ----------
@app.get("/stats")
def stats(_=Depends(auth)):
    try:
        conn = _conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM patients")
        n = cur.fetchone()[0]
    except Exception:
        n = 0
    return {"patients": n}

# ---------- NEW: Round-trip export from System B ----------
@app.get("/patients/{pid}/passport")
def export_passport(pid: str, _=Depends(auth)):
    """
    Re-export the patient we previously imported (minimal bundle),
    so you can compare A → B → (export) with A’s original JSON.
    """
    conn = _conn()
    ensure_tables(conn)
    row = get_patient(conn, pid)
    if not row:
        raise HTTPException(status_code=404, detail="Patient not found in System B")

    pid, name, birth = row
    # Reconstruct a minimal DMP bundle (same shape you import)
    bundle = {
        "passportVersion": "0.1",
        "patient": {
            "resourceType": "Patient",
            "id": pid,
            "name": [{"text": name}] if name else [],
            "birthDate": birth or ""
        },
        "medications": [],
        "immunizations": [],
        "encounters": [],
        "observations": []
    }
    return bundle
