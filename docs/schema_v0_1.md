# DMP v0.1 — Minimal EMIS-Aligned Data Model (MVP)

This is the **minimum** schema needed to build a working Digital Medical Passport prototype.  
It follows the EMIS Extended Dataset field names where possible and keeps only essential columns.

---

## 1) Entities included (MVP)
- **Patient** (core identity)
- **Appointment** (basic visit history)
- **Medication** (active/past meds)
- **Event** (observations / immunisations / allergies in one table for v0)

*Later (v1.0, optional):* **Problem**, **MedicationIssue** (only if time permits).

---

## 2) Keys & Relationships

### Primary Keys (PK)
- Patient: `PatientGuid` (UUID string)
- Appointment: `AppointmentGuid` (UUID string)
- Medication: `MedicationGuid` (UUID string)
- Event: `EventGuid` (UUID string)

### Foreign Keys (FK)
- Appointment.`PatientGuid` → Patient.`PatientGuid`
- Medication.`PatientGuid` → Patient.`PatientGuid`
- Event.`PatientGuid` → Patient.`PatientGuid`

### ER (text)
