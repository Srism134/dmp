## 3) Relationships

- Patient (1) — (Many) Appointment via PatientGuid
- Patient (1) — (Many) Medication via PatientGuid
- Patient (1) — (Many) Event via PatientGuid

**Cardinality:** Patient is the parent; Appointment/Medication/Event are children.

### Quick ERD (text)
Patient (PatientGuid PK)
  ├─< Appointment (AppointmentGuid PK, PatientGuid FK)
  ├─< Medication   (MedicationGuid  PK, PatientGuid FK)
  └─< Event        (EventGuid       PK, PatientGuid FK)
