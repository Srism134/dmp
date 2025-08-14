import csv
import os
import glob

# Folder where CSVs are stored
LOOKUP_DIR = os.path.join("data", "lookups")

def validate_csv(file_path):
    print(f"\nValidating {file_path}...")
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            rows = list(reader)

            # Check for empty file
            if not rows:
                print(" File is empty!")
                return

            # Check for missing values
            for i, row in enumerate(rows, start=1):
                for col, val in row.items():
                    if val.strip() == "":
                        print(f"  Missing value in row {i}, column '{col}'")

            print(f" {len(rows)} rows validated OK.")

    except Exception as e:
        print(f" Error reading {file_path}: {e}")

def main():
    csv_files = glob.glob(os.path.join(LOOKUP_DIR, "*.csv"))
    if not csv_files:
        print(" No CSV files found in lookups directory!")
        return

    for file_path in csv_files:
        validate_csv(file_path)

if __name__ == "__main__":
    main()
