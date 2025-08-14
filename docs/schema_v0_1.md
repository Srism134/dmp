## Acceptance Criteria (MVP)

- At least **50** Patients.
- Each patient has **1–5** appointments, **0–3** medications, **0–5** events.
- All foreign keys are valid (no orphan records).
- Coded fields only use values from lookup CSVs.
- All dates are sensible:
  - Date of Birth is in the past.
  - Appointments fall in realistic time windows.

## Appendix: SQLite DDL (MVP)

> This is for reference only — we will not run this yet.

```sql
CREATE TABLE Patient (
    PatientGuid TEXT PRIMARY KEY,
    Forenames TEXT NOT NULL,
    Surname TEXT NOT NULL,
    DateOfBirth DATE NOT NULL,
    Sex TEXT NOT NULL CHECK(Sex IN ('F','M','U','I')),
    PostCode TEXT,
    Ethnicity TEXT,
    PatientType INTEGER NOT NULL,
    PatientStatus INTEGER NOT NULL,
    NHSNumber TEXT
);

CREATE TABLE Appointment (
    AppointmentGuid TEXT PRIMARY KEY,
    PatientGuid TEXT NOT NULL,
    StartDateTime TEXT NOT NULL,
    EndDateTime TEXT NOT NULL,
    CurrentStatus INTEGER NOT NULL,
    SessionLocation TEXT,
    FOREIGN KEY (PatientGuid) REFERENCES Patient(PatientGuid)
);

CREATE TABLE Medication (
    MedicationGuid TEXT PRIMARY KEY,
    PatientGuid TEXT NOT NULL,
    Term TEXT NOT NULL,
    Dosage TEXT,
    PrescriptionType INTEGER NOT NULL,
    DrugStatus INTEGER NOT NULL,
    EffectiveDateTime TEXT NOT NULL,
    FOREIGN KEY (PatientGuid) REFERENCES Patient(PatientGuid)
);

CREATE TABLE Event (
    EventGuid TEXT PRIMARY KEY,
    PatientGuid TEXT NOT NULL,
    EventType INTEGER NOT NULL,
    Term TEXT NOT NULL,
    ReadCode TEXT,
    SnomedCTCode TEXT,
    EffectiveDateTime TEXT NOT NULL,
    FOREIGN KEY (PatientGuid) REFERENCES Patient(PatientGuid)
);
