import sqlite3

conn = sqlite3.connect("dmp.db")
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("Total patients:", c.execute("SELECT COUNT(*) FROM patients").fetchone()[0])

print("\nTop 5 patients by appointment count:")
for r in c.execute("""
    SELECT p.Surname, p.Forenames, COUNT(a.AppointmentGuid) AS appt_count
    FROM patients p
    LEFT JOIN appointments a ON a.PatientGuid = p.PatientGuid
    GROUP BY p.PatientGuid
    ORDER BY appt_count DESC
    LIMIT 5
"""):
    print(dict(r))

conn.close()
