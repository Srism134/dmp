import sqlite3
from pathlib import Path

# Paths
db_path = Path("medical.db")
schema_path = Path("docs/schema.sql")

# Delete old DB if exists
if db_path.exists():
    db_path.unlink()

# Read schema.sql
sql = schema_path.read_text(encoding="utf-8")

# Create DB + apply schema
db = sqlite3.connect(db_path)
db.executescript(sql)
db.commit()
db.close()

print(" medical.db created and schema applied from docs/schema.sql")
