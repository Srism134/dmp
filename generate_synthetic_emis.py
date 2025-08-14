import csv, os, random, uuid
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from faker import Faker

# === settings ===
OUT_DIR = "data"
LOOKUPS_DIR = "data/lookups_mvp"   # <- use the MVP lookups we just made
N_PATIENTS   = 50                  # default; you can override via CLI
SEED         = 42                  # for reproducibility

fake = Faker("en_GB")
random.seed(SEED)
Faker.seed(SEED)

# ---------- helpers ----------
def read_lookup(path, has_header=True):
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        if has_header:
            next(reader, None)
        for row in reader:
            if not row: 
                continue
            out.append(row)
    return out

def choice_from_lookup(rows):
    # takes [['id','label'], ...] already headerless
    return random.choice(rows)[0]

def safe_mkdir(p):
    os.makedirs(p, exist_ok=True)

def rand_dt_between(start_dt, end_dt):
    delta = end_dt - start_dt
    seconds = delta.total_seconds()
    r = random.random() * seconds
    return start_dt + timedelta(seconds=r)

def fake_nhs_number():
    # 10-digit fake; no real validation needed for demo
    base = [random.randint(0, 9) for _ in range(9)]
    check = random.randint(0, 9)
    return "".join(str(d) for d in base) + str(check)

# ---------- load lookups ----------
sex_lkp            = read_lookup(os.path.join(LOOKUPS_DIR, "sex.csv"))
patient_status_lkp = read_lookup(os.path.join(LOOKUPS_DIR, "patient_status.csv"))
patient_type_lkp   = read_lookup(os.path.join(LOOKUPS_DIR, "patient_type.csv"))
event_type_lkp     = read_lookup(os.path.join(LOOKUPS_DIR, "event_type.csv"))
presc_type_lkp     = read_lookup(os.path.join(LOOKUPS_DIR, "prescription_type.csv"))
drug_status_lkp    = read_lookup(os.path.join(LOOKUPS_DIR, "drug_status.csv"))
appt_status_lkp    = read_lookup(os.path.join(LOOKUPS_DIR, "appointment_status.csv"))

# ---------- output paths ----------
safe_mkdir(OUT_DIR)
patients_path     = os.path.join(OUT_DIR, "patients.csv")
appointments_path = os.path.join(OUT_DIR, "appointments.csv")
medications_path  = os.path.join(OUT_DIR, "medications.csv")
events_path       = os.path.join(OUT_DIR, "events.csv")

# ---------- generate patients ----------
patients = []
for _ in range(N_PATIENTS):
    pid = str(uuid.uuid4())
    dob = fake.date_of_birth(minimum_age=0, maximum_age=100)
    patients.append({
        "PatientGuid": pid,
        "Forenames": fake.first_name(),
        "Surname": fake.last_name(),
        "DateOfBirth": dob.isoformat(),
        "Sex": choice_from_lookup(sex_lkp),
        "PostCode": fake.postcode().replace(" ", ""),
        "Ethnicity": random.choice(["", "White", "Asian", "Black", "Mixed", "Other"]),
        "PatientType": choice_from_lookup(patient_type_lkp),
        "PatientStatus": choice_from_lookup(patient_status_lkp),
        "NHSNumber": fake_nhs_number()
    })

# ---------- generate appointments / meds / events ----------
appointments = []
medications  = []
events       = []

now = datetime.now()
start_window = now - relativedelta(years=5)
end_window   = now + relativedelta(months=6)

for p in patients:
    pid = p["PatientGuid"]

    # appointments: 1–5 each
    for _ in range(random.randint(1, 5)):
        start = rand_dt_between(start_window, now)
        end   = start + timedelta(minutes=random.choice([10, 15, 20, 30]))
        appointments.append({
            "AppointmentGuid": str(uuid.uuid4()),
            "PatientGuid": pid,
            "StartDateTime": start.isoformat(timespec="seconds"),
            "EndDateTime":   end.isoformat(timespec="seconds"),
            "CurrentStatus": choice_from_lookup(appt_status_lkp),
            "SessionLocation": random.choice(["GP Surgery A", "GP Surgery B", "Walk-In Centre", "Telephone"])
        })

    # medications: 0–3 each
    for _ in range(random.randint(0, 3)):
        term = random.choice([
            "Amoxicillin 500mg capsule",
            "Paracetamol 500mg tablet",
            "Ibuprofen 200mg tablet",
            "Atorvastatin 20mg tablet",
            "Lisinopril 10mg tablet"
        ])
        medications.append({
            "MedicationGuid": str(uuid.uuid4()),
            "PatientGuid": pid,
            "Term": term,
            "Dosage": random.choice([
                "1 tablet twice daily",
                "500 mg three times daily",
                "10 mg once daily",
                "200 mg as needed"
            ]),
            "PrescriptionType": choice_from_lookup(presc_type_lkp),
            "DrugStatus": choice_from_lookup(drug_status_lkp),
            "EffectiveDateTime": rand_dt_between(start_window, now).isoformat(timespec="seconds")
        })

    # events: 1–6 each (observations / allergy / immunisation)
    for _ in range(random.randint(1, 6)):
        et = int(choice_from_lookup(event_type_lkp))
        # simple term suggestions per type
        if   et == 1:  term = random.choice(["BP systolic", "BP diastolic", "Pulse rate", "Temperature"])
        elif et == 11: term = random.choice(["Penicillin allergy", "Peanut allergy", "Latex allergy"])
        elif et == 13: term = random.choice(["COVID-19 vaccine", "Influenza vaccine", "MMR vaccine"])
        else:          term = "Clinical note"

        events.append({
            "EventGuid": str(uuid.uuid4()),
            "PatientGuid": pid,
            "EventType": et,
            "Term": term,
            "ReadCode": "",          # optional in MVP
            "SnomedCTCode": "",      # optional in MVP
            "EffectiveDateTime": rand_dt_between(start_window, now).isoformat(timespec="seconds")
        })

# ---------- write CSVs ----------
def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

write_csv(patients_path,
          ["PatientGuid","Forenames","Surname","DateOfBirth","Sex","PostCode","Ethnicity","PatientType","PatientStatus","NHSNumber"],
          patients)

write_csv(appointments_path,
          ["AppointmentGuid","PatientGuid","StartDateTime","EndDateTime","CurrentStatus","SessionLocation"],
          appointments)

write_csv(medications_path,
          ["MedicationGuid","PatientGuid","Term","Dosage","PrescriptionType","DrugStatus","EffectiveDateTime"],
          medications)

write_csv(events_path,
          ["EventGuid","PatientGuid","EventType","Term","ReadCode","SnomedCTCode","EffectiveDateTime"],
          events)

print(f"OK  Generated {len(patients)} patients, {len(appointments)} appointments, {len(medications)} meds, {len(events)} events.")
print(f"Files saved under: {OUT_DIR}\\")
