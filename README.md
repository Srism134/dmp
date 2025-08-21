# Digital Medical Passport Project
## Entity–Relationship Diagram (ERD)

```mermaid
erDiagram
    PATIENT ||--o{ APPOINTMENT : has
    PATIENT ||--o{ MEDICATION : takes
    PATIENT ||--o{ EVENT : experiences
    PATIENT ||--o{ IMMUNISATION : receives

    PATIENT {
        string guid PK
        string name
        date dob
    }
    APPOINTMENT {
        int id PK
        date date
        string doctor
        string reason
        string patient_guid FK
    }
    MEDICATION {
        int id PK
        string drug_name
        string dose
        date start_date
        date end_date
        string patient_guid FK
    }
    EVENT {
        int id PK
        string type
        date date
        string details
        string patient_guid FK
    }
    IMMUNISATION {
        int id PK
        string vaccine
        date date
        string patient_guid FK
    }


# Digital Medical Passport (DMP)

Two goals:
1) Demonstrate a minimal FastAPI that reads from `medical.db`.
2) Show DMP export/import + patient endpoints.

## Quick start (local)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt

# create DB and load data
python scripts/init_db.py
python scripts/load_data.py

# run API
uvicorn app.main:app --host 0.0.0.0 --port 8000
