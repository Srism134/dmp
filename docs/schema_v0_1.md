# DMP v0.1 — Minimal EMIS-Aligned Schema (Planning Notes)

## 1) Tables (MVP)

### Patient
- **PK:** PatientGuid (UUID)
- **Keep:** Forenames, Surname, DateOfBirth (YYYY-MM-DD), Sex (F/M/I/U), PostCode, Ethnicity, EthnicityCode,
  PatientType (lookup), PatientStatus (lookup), NHSNumber (fake/blank allowed), RegistrationStartDate (optional)

### Appointment
- **PK:** AppointmentGuid (UUID)
- **FK:** PatientGuid → Patient.PatientGuid
- **Keep:** StartDateTime, EndDateTime, CurrentStatus (lookup), SessionLocation

### Medication
- **PK:** MedicationGuid (UUID)
- **FK:** PatientGuid → Patient.PatientGuid
- **Keep:** Term, Dosage, PrescriptionType (1 Acute | 2 Repeat | 3 Repeat Dispensed | 4 Automatic),
  DrugStatus (1 Current | 2 Past | 3 Never Active), EffectiveDateTime

### MedicationIssue (add later if needed)
- **PK:** MedicationIssueGuid (UUID)
- **FK:** MedicationGuid, PatientGuid
- **Keep later:** EffectiveDateTime, IssueMethod

### Event  (observations/immunisations/allergies/etc.)
- **PK:** EventGuid (UUID)
- **FK:** PatientGuid → Patient.PatientGuid
- **Keep:** EventType (lookup), Term, ReadCode (opt), SnomedCTCode (opt), EffectiveDateTime, IsAbnormal (0/1)

### Problem (diagnoses/conditions) — optional in v0
- **PK:** ProblemGuid (UUID)
- **FK:** PatientGuid → Patient.PatientGuid
- **Keep:** Term, ReadCode, SnomedCTCode, Status, Significance, EffectiveDateTime, EndDate (nullable)

---

## 2) Relationships
- Patient (1) — (M) Appointment
- Patient (1) — (M) Medication
- Patient (1) — (M) Event
- Patient (1) — (M) Problem
- Medication (1) — (M) MedicationIssue  *(if used later)*

---

## 3) Lookups (subset used in v0)

### Sex
- F = Female
- M = Male
- I = Indeterminate
- U = Unknown

### PatientStatus (examples)
- 1 = Patient has presented
- 8 = Correctly registered
- 11 = Death
*(others available in data/lookups/patient_status.csv)*

### PatientType (examples)
- 4 = Regular
- 12 = Walk-In Patient
*(others in data/lookups/patient_type.csv)*

### EventType (examples)
- 1 = Observation
- 11 = Allergy
- 13 = Immunisation
*(others in data/lookups/event_type.csv)*

### PrescriptionType
- 1 = Acute
- 2 = Repeat
- 3 = Repeat Dispensed
- 4 = Automatic

### DrugStatus
- 1 = Current
- 2 = Past
- 3 = Never Active

### Appointment CurrentStatus (examples)
- 2 = Arrived
- 4 = Left
- 5 = DNA
- 9 = Telephone — Complete
*(full list in data/lookups/appt_status.csv)*

---

## 4) Acceptance for Phase 1 complete
- ✅ Tables selected + essential columns listed
- ✅ Primary/Foreign keys defined
- ✅ Lookups chosen and stored in CSVs under data/lookups/
- ✅ Relationships documented
- ⛳ Ready to generate synthetic data (Phase 2)

