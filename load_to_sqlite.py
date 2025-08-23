# load_to_sqlite.py
import csv, sqlite3
from pathlib import Path

DATA = Path("data")
DB_PATH = "dmp.db"

# --- DDL (schema) ---
DDL = [
    "PRAGMA foreign_keys=ON;",
    "DROP TABLE IF EXISTS appointments;",
    "DROP TABLE IF EXISTS medications;",
    "DROP TABLE IF EXISTS events;",
    "DROP TABLE IF EXISTS patients;",
    """
    CREATE TABLE patients (
        PatientGuid TEXT PRIMARY KEY,
        Forenames TEXT NOT NULL,
        Surname TEXT NOT NULL,
        DateOfBirth TEXT NOT NULL,   -- YYYY-MM-DD
        Sex TEXT NOT NULL,           -- F/M/U/I
        PostCode TEXT,
        Ethnicity TEXT,
        PatientType INTEGER NOT NULL,
        PatientStatus INTEGER NOT NULL,
        NHSNumber TEXT               -- fake or blank
    );
    """,
    """
    CREATE TABLE appointments (
        AppointmentGuid TEXT PRIMARY KEY,
        PatientGuid TEXT NOT NULL,
        StartDateTime TEXT NOT NULL,
        EndDateTime   TEXT NOT NULL,
        CurrentStatus INTEGER NOT NULL,
        SessionLocation TEXT,
        FOREIGN KEY (PatientGuid) REFERENCES patients(PatientGuid) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE medications (
        MedicationGuid TEXT PRIMARY KEY,
        PatientGuid TEXT NOT NULL,
        Term TEXT NOT NULL,
        Dosage TEXT,
        PrescriptionType INTEGER NOT NULL,   -- 1..4
        DrugStatus INTEGER NOT NULL,         -- 1..3
        EffectiveDateTime TEXT NOT NULL,
        FOREIGN KEY (PatientGuid) REFERENCES patients(PatientGuid) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE events (
        EventGuid TEXT PRIMARY KEY,
        PatientGuid TEXT NOT NULL,
        EventType INTEGER NOT NULL,  -- 1,11,13
        Term TEXT NOT NULL,
        ReadCode TEXT,
        SnomedCTCode TEXT,
        EffectiveDateTime TEXT NOT NULL,
        FOREIGN KEY (PatientGuid) REFERENCES patients(PatientGuid) ON DELETE CASCADE
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_appt_patient ON appointments(PatientGuid);",
    "CREATE INDEX IF NOT EXISTS idx_med_patient  ON medications(PatientGuid);",
    "CREATE INDEX IF NOT EXISTS idx_evt_patient  ON events(PatientGuid);",
]

def load_csv_rows(path: Path, columns):
    with open(path, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = [tuple((r0.get(c, "") or "").strip() for c in columns) for r0 in r]
    return rows

def insert_many(conn, table, columns, rows):
    q = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({','.join('?'*len(columns))})"
    conn.executemany(q, rows)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON;")

    # Create schema
    for stmt in DDL:
        conn.execute(stmt)

    # Load data
    patients_cols = ["PatientGuid","Forenames","Surname","DateOfBirth","Sex","PostCode",
                     "Ethnicity","PatientType","PatientStatus","NHSNumber"]
    appts_cols    = ["AppointmentGuid","PatientGuid","StartDateTime","EndDateTime","CurrentStatus","SessionLocation"]
    meds_cols     = ["MedicationGuid","PatientGuid","Term","Dosage","PrescriptionType","DrugStatus","EffectiveDateTime"]
    events_cols   = ["EventGuid","PatientGuid","EventType","Term","ReadCode","SnomedCTCode","EffectiveDateTime"]

    patients_rows = load_csv_rows(DATA/"patients.csv", patients_cols)
    appts_rows    = load_csv_rows(DATA/"appointments.csv", appts_cols)
    meds_rows     = load_csv_rows(DATA/"medications.csv", meds_cols)
    events_rows   = load_csv_rows(DATA/"events.csv", events_cols)

    insert_many(conn, "patients", patients_cols, patients_rows)
    insert_many(conn, "appointments", appts_cols, appts_rows)
    insert_many(conn, "medications", meds_cols, meds_rows)
    insert_many(conn, "events", events_cols, events_rows)

    conn.commit()

    # Quick integrity checks
    cur = conn.cursor()
    counts = {}
    for t in ("patients","appointments","medications","events"):
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        counts[t] = cur.fetchone()[0]
    print("Counts:", counts)

    # Orphan check
    for t in ("appointments","medications","events"):
        cur.execute(f"""
          SELECT COUNT(*)
          FROM {t} c
          LEFT JOIN patients p ON p.PatientGuid = c.PatientGuid
          WHERE p.PatientGuid IS NULL
        """)
        missing = cur.fetchone()[0]
        if missing:
            print(f"WARNING: {missing} {t} rows have no matching PatientGuid")
        else:
            print(f"OK: all {t} rows reference valid patients")

    # Sample join
    cur.execute("""
      SELECT p.Surname, p.Forenames, COUNT(a.AppointmentGuid) AS appts
      FROM patients p
      LEFT JOIN appointments a ON a.PatientGuid = p.PatientGuid
      GROUP BY p.PatientGuid
      ORDER BY appts DESC, p.Surname
      LIMIT 5
    """)
    print("\nTop 5 patients by appointment count:")
    for row in cur.fetchall():
        print(row)

    conn.close()
    print("\nLoaded CSVs into dmp.db ")

if __name__ == "__main__":
    main()
