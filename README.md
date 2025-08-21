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


