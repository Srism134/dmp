import sqlite3
import faker
import random
from datetime import datetime, timedelta

fake = faker.Faker()

def seed_data(db_path="medical.db", num_patients=10):
    db = sqlite3.connect(db_path)
    cur = db.cursor()

    # ----- Patients (patient_id, name, dob, gender) -----
    patients = []
    for _ in range(num_patients):
        guid = fake.uuid4()
        full_name = fake.name()
        dob = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime("%Y-%m-%d")
        gender = random.choice(["Male", "Female", "Other"])
        patients.append((guid, full_name, dob, gender))
    cur.executemany(
        "INSERT INTO Patients (patient_id, name, dob, gender) VALUES (?,?,?,?)",
        patients
    )

    # ----- Appointments (appointment_id, patient_id, date, doctor, reason) -----
    appts = []
    for (patient_id, *_rest) in patients:
        for _ in range(random.randint(1, 3)):
            appt_id = fake.uuid4()
            date = (datetime.now() + timedelta(days=random.randint(-365, 365))).strftime("%Y-%m-%d")
            doctor = fake.name()
            reason = random.choice(["Checkup", "Follow-up", "Consultation", "Vaccination", "Flu symptoms"])
            appts.append((appt_id, patient_id, date, doctor, reason))
    cur.executemany(
        "INSERT INTO Appointments (appointment_id, patient_id, date, doctor, reason) VALUES (?,?,?,?,?)",
        appts
    )

    # ----- Medications (medication_id, patient_id, drug_name, dose, start_date, end_date) -----
    meds = []
    for (patient_id, *_rest) in patients:
        for _ in range(random.randint(1, 3)):
            med_id = fake.uuid4()
            drug = random.choice(["Paracetamol", "Ibuprofen", "Amoxicillin", "Metformin", "Atorvastatin"])
            dose = random.choice(["500mg", "250mg", "5mg", "10mg"])
            start = (datetime.now() - timedelta(days=random.randint(10, 400))).strftime("%Y-%m-%d")
            end = (datetime.now() + timedelta(days=random.randint(0, 200))).strftime("%Y-%m-%d")
            meds.append((med_id, patient_id, drug, dose, start, end))
    cur.executemany(
        "INSERT INTO Medications (medication_id, patient_id, drug_name, dose, start_date, end_date) VALUES (?,?,?,?,?,?)",
        meds
    )

    # ----- Events (event_id, patient_id, event_type, description, date) -----
    events = []
    for (patient_id, *_rest) in patients:
        for _ in range(random.randint(1, 2)):
            ev_id = fake.uuid4()
            ev_type = random.choice(["Admission", "Surgery", "Allergy"])
            desc = fake.sentence(nb_words=8)
            ev_date = (datetime.now() - timedelta(days=random.randint(1, 800))).strftime("%Y-%m-%d")
            events.append((ev_id, patient_id, ev_type, desc, ev_date))
    cur.executemany(
        "INSERT INTO Events (event_id, patient_id, event_type, description, date) VALUES (?,?,?,?,?)",
        events
    )

    # ----- Immunisations (immunisation_id, patient_id, vaccine, date, provider) -----
    immunisations = []
    for (patient_id, *_rest) in patients:
        for _ in range(random.randint(0, 2)):
            im_id = fake.uuid4()
            vaccine = random.choice(["COVID-19", "Influenza", "Hepatitis B", "Tetanus"])
            im_date = (datetime.now() - timedelta(days=random.randint(30, 1500))).strftime("%Y-%m-%d")
            provider = fake.company()
            immunisations.append((im_id, patient_id, vaccine, im_date, provider))
    cur.executemany(
        "INSERT INTO Immunisations (immunisation_id, patient_id, vaccine, date, provider) VALUES (?,?,?,?,?)",
        immunisations
    )

    db.commit()
    db.close()
    print(" Synthetic data loaded!")

if __name__ == "__main__":
    seed_data()
