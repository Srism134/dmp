# verify_db.py
import sqlite3, json

# Connect to the SQLite database
con = sqlite3.connect("dmp.db")
con.execute("PRAGMA foreign_keys = ON;")
cur = con.cursor()

def count(tbl):
    return cur.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]

# Count rows in each main table
summary = {
    "patients": count("patients"),
    "appointments": count("appointments"),
    "medications": count("medications"),
    "events": count("events"),
}

# Check for foreign key violations
fk_violations = cur.execute("PRAGMA foreign_key_check;").fetchall()

# Simple join test: top 5 patients by appointment count
top_appt = cur.execute("""
  SELECT p.Surname, p.Forenames, COUNT(a.AppointmentGuid) AS appt_count
  FROM patients p LEFT JOIN appointments a
    ON a.PatientGuid = p.PatientGuid
  GROUP BY p.PatientGuid
  ORDER BY appt_count DESC
  LIMIT 5;
""").fetchall()

print("Row counts:", json.dumps(summary, indent=2))
print("FK violations:", fk_violations if fk_violations else "None")
print("Top 5 by appointments:", top_appt)

con.close()
