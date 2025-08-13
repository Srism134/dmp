## Minimum Viable Data Model (MVP)

### Patient
- PatientGuid (UUID, PK)
- Forenames (text)
- Surname (text)
- DateOfBirth (date)
- Sex (code: F/M/U/I)
- PostCode (text)
- Ethnicity (text, optional)
- PatientType (int; from lookup)
- PatientStatus (int; from lookup)
- NHSNumber (text; fake or null allowed)

### Appointment
- AppointmentGuid (UUID, PK)
- PatientGuid (UUID, FK→Patient)
- StartDateTime (datetime)
- EndDateTime (datetime)
- CurrentStatus (int; from lookup)
- SessionLocation (text)

### Medication
- MedicationGuid (UUID, PK)
- PatientGuid (UUID, FK→Patient)
- Term (text; e.g., “Amoxicillin 500mg cap”)
- Dosage (text; e.g., “500 mg TID for 5 days”)
- PrescriptionType (int; 1=Acute, 2=Repeat, 3=Repeat Dispensed, 4=Automatic)
- DrugStatus (int; 1=Current, 2=Past, 3=Never Active)
- EffectiveDateTime (datetime)

### Event (use for observations/immunisations/allergies etc.)
- EventGuid (UUID, PK)
- PatientGuid (UUID, FK→Patient)
- EventType (int; e.g., 1=Observation, 11=Allergy, 13=Immunisation)
- Term (text; e.g., “COVID-19 vaccine”, “Penicillin allergy”, “BP systolic”)
- ReadCode (text, optional)
- SnomedCTCode (text, optional)
- EffectiveDateTime (datetime)
