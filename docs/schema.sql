PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS Patients(
  patient_id   TEXT PRIMARY KEY,
  name         TEXT NOT NULL,
  dob          DATE NOT NULL,
  gender       TEXT
);

CREATE TABLE IF NOT EXISTS Appointments(
  appointment_id TEXT PRIMARY KEY,
  patient_id     TEXT NOT NULL REFERENCES Patients(patient_id) ON DELETE CASCADE,
  date           DATE NOT NULL,
  doctor         TEXT,
  reason         TEXT
);

CREATE TABLE IF NOT EXISTS Medications(
  medication_id TEXT PRIMARY KEY,
  patient_id    TEXT NOT NULL REFERENCES Patients(patient_id) ON DELETE CASCADE,
  drug_name     TEXT NOT NULL,
  dose          TEXT,
  start_date    DATE,
  end_date      DATE
);

CREATE TABLE IF NOT EXISTS Events(
  event_id   TEXT PRIMARY KEY,
  patient_id TEXT NOT NULL REFERENCES Patients(patient_id) ON DELETE CASCADE,
  event_type TEXT NOT NULL,   -- Admission, Surgery, Allergy, etc.
  description TEXT,
  date        DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS Immunisations(
  immunisation_id TEXT PRIMARY KEY,
  patient_id      TEXT NOT NULL REFERENCES Patients(patient_id) ON DELETE CASCADE,
  vaccine         TEXT NOT NULL,
  date            DATE NOT NULL,
  provider        TEXT
);
